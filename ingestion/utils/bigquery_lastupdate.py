from google.cloud import bigquery
from ingestion.utils.logging import get_logger


## This utility supports incremental ingestion by retrieving the latest
## creation_timestamp from BigQuery for a given data source.
##
## Depending on downstream use cases, repeated ingestion may be preferred
## (e.g., for building a historical resource log rather than a point-in-time inventory).


#Initialize logger
logger = get_logger()

def get_last_items(gcp_project_id, TABLE_NAME, config):
    #Returns latest created_timestamp from the BigQuery table based on the DATA_SOURCE

    #Initialize BigQuery client using configured project
    client = bigquery.Client(project=config.DATA_PROJECT_ID)

    #Build query to get latest creation timestamp
    query = f"""
        SELECT MAX(TIMESTAMP(creation_timestamp)) AS last_ts
        FROM `{config.DATA_PROJECT_ID}.{config.DATASET_NAME}.{TABLE_NAME}`
        WHERE project_id = @gcp_project_id
    """

    #Configure query parameters
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("gcp_project_id", "STRING", gcp_project_id)
        ]
    )

    logger.info(f"Querying table: {TABLE_NAME}")

    try:
        #Execute query
        result = client.query(query, job_config=job_config).result()

        #Return the latest creation_timestamp for the given project and table
        for row in result:
            logger.info(f"{gcp_project_id} last created_timestamp: {row.last_ts}")
            return row.last_ts
        
        logger.info(f"For {gcp_project_id}, no existing records found in {TABLE_NAME}")
        return None

    except Exception as e:
        logger.warning(f"{gcp_project_id} failed to fetch last_ts: {e}")
        return None