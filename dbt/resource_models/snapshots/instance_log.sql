{% snapshot snap_instances %}

{{
    config(
        target_schema='stl_resource_log',
        unique_key='instance_id',
        strategy='check',
        check_cols=[
            'project_id',
            'name',
            'status',
            'machine_type',
            'zone',
            'creation_timestamp',
            'last_start_timestamp',
            'last_stop_timestamp',
            'internal_ip',
            'usage_label',
            'function_label'
        ]
    )
}}

SELECT
    project_id,
    instance_id,
    name,
    status,
    machine_type,
    zone,
    creation_timestamp,
    last_start_timestamp,
    last_stop_timestamp,
    internal_ip,
    usage_label,
    function_label,
    ingested_at
FROM {{ ref('latest_instances') }}

{% endsnapshot %}