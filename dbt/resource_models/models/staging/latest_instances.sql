SELECT *
FROM (
    SELECT *,
           ROW_NUMBER() OVER (
               PARTITION BY instance_id
               ORDER BY ingested_at DESC
           ) AS rn
    FROM `***-prod****.stl_resource_log.instance_data_import`
)
WHERE rn = 1
