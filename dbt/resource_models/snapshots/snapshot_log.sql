{% snapshot snap_snapshots %}

{{
    config(
        target_schema='stl_resource_log',
        unique_key='snapshot_id',
        strategy='check',
        check_cols=[
            'project_id',
            'name',
            'status',
            'disk_size_gb',
            'creation_timestamp',
            'source_disk',
            'storage_bytes',
            'region',
            'usage_label',
            'function_label'
        ]
    )
}}

SELECT
    project_id,
    snapshot_id,
    name,
    status,
    disk_size_gb,
    creation_timestamp,
    source_disk,
    storage_bytes,
    region,
    usage_label,
    function_label,
    ingested_at
FROM {{ ref('latest_snapshots') }}

{% endsnapshot %}