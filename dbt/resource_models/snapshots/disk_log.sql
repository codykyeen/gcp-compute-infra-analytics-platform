{% snapshot snap_disks %}

{{
    config(
        target_schema='stl_resource_log',
        unique_key='disk_id',
        strategy='check',
        check_cols=[
            'project_id',
            'name',
            'size_gb',
            'type',
            'zone',
            'attached_instance',
            'creation_timestamp',
            'usage_label',
            'function_label'
        ]
    )
}}

SELECT
    project_id,
    disk_id,
    name,
    size_gb,
    type,
    zone,
    attached_instance,
    usage_label,
    creation_timestamp,
    function_label,
    ingested_at
FROM {{ ref('latest_disks') }}

{% endsnapshot %}