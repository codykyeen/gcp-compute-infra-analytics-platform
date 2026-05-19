{{ config(
    materialized='table',
    cluster_by=["project_id"]
) }}

WITH instances AS (
    SELECT
        project_id,
        instance_id,
        name as instance_name,
        zone,
        name
    FROM {{ ref('latest_instances') }}
),

disks AS (
    SELECT
        project_id,
        disk_id,
        name as disk_name,
        attached_instance as instance_name
    FROM {{ ref('latest_disks') }}
),

snapshots AS (
    SELECT
        project_id,
        snapshot_id,
        name as snapshot_name,
        SPLIT(source_disk, '/')[OFFSET(ARRAY_LENGTH(SPLIT(source_disk, '/')) - 1)] as disk_name
    FROM {{ ref('latest_snapshots') }}
),

--Count disks per instance
instance_disks AS (
    SELECT
        instance_name,
        COUNT(*) AS disk_count
    FROM disks
    GROUP BY instance_name
),

final AS (
    SELECT
        i.project_id,
        i.zone,
        COUNT(DISTINCT i.instance_id) AS total_instances,
        COUNT(DISTINCT d.disk_id) AS total_disks,
        COUNT(DISTINCT s.snapshot_id) AS total_snapshots,
        AVG(COALESCE(id.disk_count, 0)) AS avg_disks_per_instance
    FROM instances i
    LEFT JOIN disks d
        ON i.instance_name = d.instance_name
    LEFT JOIN snapshots s
        ON d.disk_name = s.disk_name
    LEFT JOIN instance_disks id
        ON i.instance_name = id.instance_name
    GROUP BY i.project_id, i.zone
)

SELECT * FROM final