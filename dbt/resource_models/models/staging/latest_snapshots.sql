SELECT *
FROM (
    SELECT *,
           ROW_NUMBER() OVER (
               PARTITION BY snapshot_id
               ORDER BY ingested_at DESC
           ) AS rn
    FROM `<gcp_project>.stl_resource_log.snapshot_data_import`
)
WHERE rn = 1
