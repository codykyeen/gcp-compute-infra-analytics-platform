
import pandas as pd
import ingestion.config as config
from datetime import datetime, timezone
from ingestion.utils.logging import get_logger

#Initialize Logging
logger = get_logger()

#Example Table
TABLE_NAME = "snapshot_data_import"

def fetch_data(config):
    #Fetches sample data for ingestion into BigQuery

    logger.info("Starting sample data ingestion")

    # Simulated Data (replace later with real API / GCP data)
    data = [
        {"project_id": "sample_run", "name": "test_name_1", "creation_timestamp": datetime.now(timezone.utc)},
        {"project_id": "sample_run", "name": "test_name_2", "creation_timestamp": datetime.now(timezone.utc)},
    ]

    #Convert raw data into pandas DataFrame
    df = pd.DataFrame(data)

    #Add ingestion timestamp for partitioning and load tracking
    ingested_at = datetime.now(timezone.utc)
    df["ingested_at"] = ingested_at

    #Return Final DataFrame
    return df, TABLE_NAME