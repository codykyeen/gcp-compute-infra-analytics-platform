from google.cloud import bigquery
from ingestion.config import DATA_PROJECT_ID, DATASET_NAME, WRITE_MODE
from ingestion.utils.logging import get_logger

#Initialize Logger
logger = get_logger()


def load_dataframe(df, TABLE_NAME):
    #Load DataFrame into BigQuery with partitioning, clustering, and schema evolution support

    #Generate table name
    table_id = f"{DATA_PROJECT_ID}.{DATASET_NAME}.{TABLE_NAME}"

    logger.info(f"Preparing BigQuery load for table: {table_id}")

    #Does not run if dataframe is empty
    if df.empty:
        logger.warning(f"No data to load into {table_id}")
        return

    #Prepare BQ Client
    client = bigquery.Client(project=DATA_PROJECT_ID)

    #Configure BQ Job
    job_config = bigquery.LoadJobConfig(
        time_partitioning=bigquery.TimePartitioning(
            type_=bigquery.TimePartitioningType.DAY,
            field="ingested_at"
        ),
        clustering_fields=["project_id"]
    )

    #Set WRITE mode
    if WRITE_MODE == "append":
        job_config.write_disposition = bigquery.WriteDisposition.WRITE_APPEND
    else:
        job_config.write_disposition = bigquery.WriteDisposition.WRITE_TRUNCATE

    job_config.autodetect = True

    #Allow new fields to be added automatically to the BQ table
    job_config.schema_update_options = [
        bigquery.SchemaUpdateOption.ALLOW_FIELD_ADDITION
    ]

    logger.info(f"Loading {len(df)} rows into {table_id} (WRITE_MODE={WRITE_MODE})")

    try:
        job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
        logger.info(f"Started BigQuery load job: {job.job_id}")
        job.result()
        logger.info(f"Load complete for {table_id}")

    except Exception:
        logger.exception(f"Failed to load data into {table_id}")
        raise
        