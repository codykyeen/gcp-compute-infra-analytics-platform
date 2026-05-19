
import importlib
import ingestion.config as config
from ingestion.loaders.bigquery import load_dataframe
from ingestion.utils.logging import get_logger

#Initialize logger
logger = get_logger()


#Log selected data source for traceability
logger.info(f"DATA_SOURCE = {config.DATA_SOURCE}")


def get_fetch_function():
    #Dynamically load the fetch function based on DATA_SOURCE

    module_name = f"ingestion.sources.{config.DATA_SOURCE}"

    try:
        module = importlib.import_module(module_name)
        return module.fetch_data
    except ModuleNotFoundError:
        raise ValueError(f"Unknown data source: {config.DATA_SOURCE}")


#Resolve fetch function at load time
fetch_data = get_fetch_function()


def run_ingestion():
    #Run ingestions pipeline for selected data source

    try:
        logger.info(f"Starting ingestion from {config.DATA_SOURCE}")

        #Fetch data and destination table
        df, TABLE_NAME = fetch_data(config)

        #Handle when no data is returned
        if df.empty:
            logger.warning("No data returned")
            return

        logger.info(f"Loading data into table: {TABLE_NAME}")

        #Loads data into BigQuery
        load_dataframe(df, TABLE_NAME)

        logger.info("Ingestion completed successfully")

    except Exception:
        logger.exception("Ingestion failed")
        raise

#Allow this script to be run directly while remaining safe for import
if __name__ == "__main__":
    run_ingestion()
