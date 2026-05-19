{{ config(
    materialized='incremental',
    partition_by={
        "field": "insert_timestamp",
        "data_type": "timestamp",
        "granularity": "day"
    },
    cluster_by=["project_id"]
) }}

SELECT
    project_id,
    disk_id,
    name as disk_name,
    zone,
    CASE WHEN attached_instance IS NULL THEN TRUE ELSE FALSE END AS orphaned,
    CURRENT_TIMESTAMP() as insert_timestamp
FROM {{ ref('latest_disks') }}
WHERE attached_instance IS NULL


{% if is_incremental() %}
  --Insert the same disk_id once per day
  AND disk_id NOT IN (
    SELECT disk_id FROM {{ this }} WHERE DATE(insert_timestamp) = DATE(CURRENT_TIMESTAMP())
  )
{% endif %}
