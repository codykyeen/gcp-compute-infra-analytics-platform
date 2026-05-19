SELECT *
FROM (
    SELECT *,
           ROW_NUMBER() OVER (
               PARTITION BY disk_id
               ORDER BY ingested_at DESC
           ) AS rn
    FROM `***-prod****.stl_resource_log.disk_data_import`
)
WHERE rn = 1
