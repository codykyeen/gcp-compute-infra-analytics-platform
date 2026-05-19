from googleapiclient.discovery import build
from ingestion.utils.logging import get_logger
from ingestion.utils.get_gcp_projects import get_active_gcp_projects
from ingestion.utils.bigquery_lastupdate import get_last_items
import pandas as pd
from datetime import datetime, timezone

#Define Import Table
TABLE_NAME = "snapshot_data_import"

#Initialize Logging
logger = get_logger()

def fetch_data(config):
    #Fetches GCP snapshot data from GCP Compute API

    compute = build("compute", "v1")

    #Get full list of Actice GCP Projects
    gcp_projects = get_active_gcp_projects(config)
    logger.info(f"Active Project List: {gcp_projects}")

    snapshots = []

    for project_id in gcp_projects:
        try:
            logger.info(f"Fetching snapshots for project: {project_id}")

            #Confirm the newest created snapshot time from the table
            last_ts = get_last_items(project_id, TABLE_NAME, config)

            #Submit request for Snapshot Data
            request = compute.snapshots().list(project=project_id)

            while request is not None:
                response = request.execute()

                for snapshot in response.get("items", []):

                    #Fetch the snapshot created time to determine if it needs to be inserted
                    snapshot_ts = pd.to_datetime(snapshot.get("creationTimestamp"))

                    #Enable to filter ingestion of any snapshots that were created before newest batch
                    ##if last_ts and snapshot_ts <= last_ts:
                    ##    continue 

                    #Get All Snapshot Labels (only inserted usage and function label at present)
                    labels = snapshot.get("labels", {})

                    #Define schema and ensure dataframe data is ready to load into BQ
                    snapshots.append({
                        "project_id": str(project_id),
                        "snapshot_id": int(snapshot.get("id")),
                        "name": str(snapshot.get("name")),
                        "status": str(snapshot.get("status")),
                        "disk_size_gb": int(snapshot.get("diskSizeGb")),
                        "creation_timestamp": snapshot_ts,
                        "source_disk": str(snapshot.get("sourceDisk")),
                        "storage_bytes": int(snapshot.get("storageBytes")),
                        "region": str(snapshot.get("region")),
                        "usage_label": labels.get("usage"),
                        "function_label": labels.get("function")
                    })

                #Move to the next item in the list
                request = compute.snapshots().list_next(
                    previous_request=request,
                    previous_response=response
                )

            logger.info(f"Collected {len(snapshots)} snapshots so far")

        except Exception as e:
            logger.error(f"Skipping project {project_id} due to error: {e}")
            continue

    if not snapshots:
        logger.warning("No snapshots found across all projects")
        return pd.DataFrame(), TABLE_NAME

    df = pd.DataFrame(snapshots)

    #Add ingestion timestamp
    ingested_at = datetime.now(timezone.utc)
    df["ingested_at"] = ingested_at

    logger.info(f"Fetched {len(df)} snapshots")

    return df, TABLE_NAME