SELECT *
FROM {{ ref('vm_full_details') }}
WHERE project_id IS NULL