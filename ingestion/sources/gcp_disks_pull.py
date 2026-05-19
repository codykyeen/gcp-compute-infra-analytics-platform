from googleapiclient.discovery import build
from ingestion.utils.logging import get_logger
from ingestion.utils.get_gcp_projects import get_active_gcp_projects
from ingestion.utils.bigquery_lastupdate import get_last_items
import pandas as pd
import json as json
from datetime import datetime, timezone

#Define Import Table
TABLE_NAME = "disk_data_import"

#Initialize Logging
logger = get_logger()

def fetch_data(config):
    #Fetches GCP disk data from GCP Compute API

    compute = build("compute", "v1")

    #Get full list of Actice GCP Projects
    gcp_projects = get_active_gcp_projects(config)
    logger.info(f"Active Project List: {gcp_projects}")

    disks = []

    for project_id in gcp_projects:

            try:
                logger.info(f"Fetching disks for project: {project_id}")

                #Confirm the newest created disk time from the table
                last_ts = get_last_items(project_id, TABLE_NAME, config)

                #Submit request for Disk Data
                request = compute.disks().aggregatedList(project=project_id)

                while request is not None:
                    response = request.execute()

                    #Enable to view the raw JSON Response for Ingestion
                    ##logger.info(json.dumps(response, indent=2))


                    for zone, zone_data in response.get("items", {}).items():

                            for disk in zone_data.get("disks", []):

                                #Fetch the disk created time to determine if it needs to be inserted
                                disk_ts = pd.to_datetime(disk.get("creationTimestamp"), utc=True)

                                #Enable to filter ingestion of any snapshots that were created before newest batch
                                ##if last_ts and disk_ts <= last_ts:
                                ##    continue
                            
                                #Fetch any instances to which the disk is attached (consider improving in case data structure changes)
                                users = disk.get("users", [])
                                attached_instance = users[0].split("/")[-1] if users else None

                                #Get All Instance Labels (only inserted usage and function label at present)
                                labels = disk.get("labels", {})

                                #Define schema and ensure dataframe data is ready to load into BQ
                                disks.append({
                                    "project_id": str(project_id),
                                    "disk_id": int(disk.get("id")),
                                    "name": str(disk.get("name")),
                                    "size_gb": int(disk.get("sizeGb")) if disk.get("sizeGb") else None,
                                    #Consider improving in case data structure changes
                                    "type": (
                                        disk.get("type").split("/")[-1]
                                        if disk.get("type") else None
                                    ),
                                    #Consider improving in case data structure changes
                                    "zone": (
                                        disk.get("zone").split("/")[-1]
                                        if disk.get("zone") else None
                                    ),
                                    "attached_instance": str(attached_instance),
                                    "creation_timestamp": disk_ts,
                                    "usage_label": labels.get("usage"),
                                    "function_label": labels.get("function")
                                })

                    #Move to the next item in the aggregated list
                    request = compute.disks().aggregatedList_next(
                        previous_request=request,
                     previous_response=response
                    )

                    logger.info(f"Collected {len(disks)} disks so far")

            except Exception as e:
                logger.error(f"Skipping project {project_id} due to error: {e}")
                continue

    if not disks:
        logger.warning("No disks found across all projects")
        return pd.DataFrame(), TABLE_NAME

    df = pd.DataFrame(disks)

    #Add ingestion timestamp
    df["ingested_at"] = datetime.now(timezone.utc)

    logger.info(f"Fetched {len(df)} disks")

    return df, TABLE_NAME