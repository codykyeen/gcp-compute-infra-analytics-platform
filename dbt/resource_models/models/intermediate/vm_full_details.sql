{{ config(
    materialized='incremental',
    partition_by={
        "field": "last_data_update",
        "data_type": "timestamp",
        "granularity": "day"
    },
    cluster_by=["project_id"]
) }}

WITH i_price AS (SELECT * FROM {{ ref('instance_pricing') }}),
    d_price AS (SELECT * FROM {{ ref('disk_pricing') }}),
    s_price AS (SELECT * FROM {{ ref('snapshot_pricing') }})

###GCP Compute Resource Summary
SELECT t1.*,
    (instance_cost_monthly + disk_cost_monthly + snapshot_cost_monthly) as machine_monthly_cost_as_conf
   FROM (
    SELECT
    i.project_id,
    i.instance_id,
    i.name as instance_name,
    i.status,
    i.machine_type,
    COALESCE((i_price.price_per_hour_usd * 730),0) as instance_cost_monthly,
    i.zone,
    i.creation_timestamp as instance_create_timestamp,
    i.last_start_timestamp as instance_last_started,
    i.last_stop_timestamp as instance_last_stopped,
    i.usage_label as instance_usage_label,
    i.function_label as instance_function_label,
    STRING_AGG(DISTINCT d.type ORDER BY d.type ASC) as disk_types,
    COUNT(DISTINCT d.type) as count_disk_types,
    STRING_AGG(DISTINCT d.name ORDER BY d.name ASC) as attached_disk_name,
    COUNT(DISTINCT d.name) as attached_disk_count,
    SUM(DISTINCT d.size_gb) as total_disk_size_gib,
    COALESCE(SUM(DISTINCT d.size_gb * d_price.price_per_gib_month),0) AS disk_cost_monthly,
    SUM(DISTINCT CASE WHEN d.type = 'pd-standard' THEN d.size_gb ELSE 0 END) AS standard_disk_size_gb,
    SUM(DISTINCT CASE WHEN d.type = 'pd-balanced' THEN d.size_gb ELSE 0 END) AS balanced_disk_size_gb,
    SUM(DISTINCT CASE WHEN d.type = 'pd-ssd' THEN d.size_gb ELSE 0 END) AS ssd_disk_size_gb,
    SUM(DISTINCT CASE WHEN d.type = 'local-ssd' THEN d.size_gb ELSE 0 END) AS local_disk_size_gb,
    STRING_AGG(DISTINCT s.name ORDER BY s.name ASC) as associated_snapshots_name,
    COUNT(DISTINCT s.name) as snapshots,
    COALESCE(SUM(DISTINCT ((s.storage_bytes/1073741824) * s_price.price_per_gib_month)),0) as snapshot_cost_monthly,
    SUM(DISTINCT (s.storage_bytes/1073741824)) as snapshots_size_gib,
    CASE WHEN STRING_AGG(DISTINCT d.usage_label) != i.usage_label THEN 'mismatch' ELSE 'match' END AS disk_usage_label_match,
    CASE WHEN STRING_AGG(DISTINCT s.usage_label) != i.usage_label THEN 'mismatch' ELSE 'match' END AS snapshot_usage_label_match,
    CASE WHEN STRING_AGG(DISTINCT d.function_label) != i.function_label THEN 'mismatch' ELSE 'match' END AS disk_function_label_match,
    CASE WHEN STRING_AGG(DISTINCT s.function_label) != i.function_label THEN 'mismatch' ELSE 'match' END AS snapshot_function_label_match,
    i.ingested_at as last_data_update,
    TO_JSON_STRING(STRUCT(
        i.project_id,
        i.name,
        i.status,
        i.machine_type,
        i.zone,
        i.creation_timestamp,
        i.last_start_timestamp,
        i.last_stop_timestamp,
        i.usage_label,
        i.function_label,
        STRING_AGG(DISTINCT d.type ORDER BY d.type ASC),
        STRING_AGG(DISTINCT d.name ORDER BY d.name ASC),
        COUNT(DISTINCT d.name),
        SUM(DISTINCT d.size_gb),
        STRING_AGG(DISTINCT s.name ORDER BY s.name ASC),
        COUNT(DISTINCT s.name),
        SUM(DISTINCT (s.storage_bytes/1073741824))
    )) AS change_hash
    FROM {{ ref('latest_instances') }} i
    LEFT JOIN {{ ref('latest_disks') }} d
    ON i.name = d.attached_instance
    LEFT JOIN {{ ref('latest_snapshots') }} s
    ON d.name = SPLIT(s.source_disk, '/')[OFFSET(ARRAY_LENGTH(SPLIT(s.source_disk, '/')) - 1)]
    LEFT JOIN i_price ON i_price.machine_type = i.machine_type
    LEFT JOIN d_price ON d_price.disk_type = d.type
    LEFT JOIN s_price ON s_price.resource_type = 'snapshot'
    GROUP BY
        i.project_id,
        i.instance_id,
        i.name,
        i.status,
        i.machine_type,
        i_price.price_per_hour_usd,
        i.zone,
        i.creation_timestamp,
        i.last_start_timestamp,
        i.last_stop_timestamp,
        i.usage_label,
        i.function_label,
        i.ingested_at
) t1
{% if is_incremental() %}
--Only insert new data
WHERE NOT EXISTS (
    SELECT 1
    FROM {{ this }} t
    WHERE t.instance_id = t1.instance_id
      AND t.change_hash = t1.change_hash
)
{% endif %}



