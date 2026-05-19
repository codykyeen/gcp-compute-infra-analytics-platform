{{ config(materialized='view') }}

WITH latest_machine_summary AS (

    SELECT *
    FROM {{ ref('vm_full_details') }}
    --only latest version per instance
    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY instance_id
        ORDER BY last_data_update DESC
    ) = 1

)

SELECT
    project_id,
    instance_id,
    instance_name,
    status,
    machine_type,
    zone,
    instance_usage_label,
    instance_function_label,
    CASE WHEN (disk_usage_label_match = 'mismatch' 
                OR snapshot_usage_label_match = 'mismatch' 
                OR disk_function_label_match = 'mismatch' 
                OR snapshot_function_label_match = 'mismatch'
            ) THEN TRUE ELSE FALSE END AS label_issue,
    attached_disk_count,
    total_disk_size_gib,
    snapshots,
    snapshots_size_gib,
    instance_cost_monthly,
    disk_cost_monthly,
    snapshot_cost_monthly,
    machine_monthly_cost_as_conf as total_monthly_cost,
    CASE WHEN attached_disk_count = 0 THEN TRUE ELSE FALSE END AS has_no_disks,
    CASE WHEN snapshots = 0 THEN TRUE ELSE FALSE END AS has_no_snapshots,
    last_data_update

FROM latest_machine_summary
