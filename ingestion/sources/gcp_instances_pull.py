from googleapiclient.discovery import build
from ingestion.utils.logging import get_logger
from ingestion.utils.get_gcp_projects import get_active_gcp_projects
from ingestion.utils.bigquery_lastupdate import get_last_items
import pandas as pd
import json as json
from datetime import datetime, timezone

#Define Import Table
TABLE_NAME = "instance_data_import"

#Initialize Logging
logger = get_logger()

def fetch_data(config):
    #Fetches GCP instance data from GCP Compute API

    compute = build("compute", "v1")

    #Get full list of Actice GCP Projects
    gcp_projects = get_active_gcp_projects(config)
    logger.info(f"Discovered {len(gcp_projects)} active projects")

    instances = []

    for project_id in gcp_projects:
            try:
                logger.info(f"Fetching instances for project: {project_id}")

                #Confirm the newest created instance time from the table
                last_ts = get_last_items(project_id, TABLE_NAME, config)

                ##Submit request for Instance Data
                logger.info(f"Querying instances API for project: {project_id}")
                request = compute.instances().aggregatedList(project=project_id)

                while request is not None:
                    response = request.execute()

                    #Enable to view the raw JSON Response for Ingestion
                    ##logger.info(json.dumps(response, indent=2))

                    for zone, zone_data in response.get("items", {}).items():

                            for instance in zone_data.get("instances", []):

                                #Fetch the instance created time to determine if it needs to be inserted
                                instance_ts = pd.to_datetime(instance.get("creationTimestamp"), utc=True)

                                #Enable to filter ingestion of any instanes that were created before newest batch
                                ##if last_ts and instance_ts <= last_ts:
                                ##    continue
                                
                                #Fetch Machine Latest Start Time (for future incremental ingesiton design considerations)
                                start_ts = (
                                    pd.to_datetime(instance.get("lastStartTimestamp"), utc=True)
                                    if instance.get("lastStartTimestamp")
                                    else None
                                )

                                #Fetch Machine Latest Start Time (for future incremental ingesiton design considerations)
                                stop_ts = (
                                    pd.to_datetime(instance.get("lastStopTimestamp"), utc=True)
                                    if instance.get("lastStopTimestamp")
                                    else None
                                )

                                #Get All Instance Labels (only inserted usage and function label at present)
                                labels = instance.get("labels", {})

                                #Get instance Internal IP
                                interfaces = instance.get("networkInterfaces", [])
                                internal_ip = interfaces[0].get("networkIP") if interfaces else None


                                #Define schema and ensure dataframe data is ready to load into BQ
                                instances.append({
                                    "project_id": str(project_id),
                                    "instance_id": int(instance.get("id")),
                                    "name": str(instance.get("name")),
                                    "status": str(instance.get("status")),
                                    "machine_type": str(instance.get("machineType").split("/")[-1]) if instance.get("machineType") else None,
                                    #Consider improving incase data structure changes
                                    "zone": str(instance.get("zone").split("/")[-1]) if instance.get("zone") else None,
                                    "creation_timestamp": instance_ts,
                                    "last_start_timestamp": start_ts,
                                    "last_stop_timestamp": stop_ts,
                                    "internal_ip": str(internal_ip),
                                    "usage_label": labels.get("usage"),
                                    "function_label": labels.get("function")
                                })

                    #Move to the next item in the aggregated list
                    request = compute.instances().aggregatedList_next(
                        previous_request=request,
                        previous_response=response
                    )

                    logger.info(f"Collected {len(instances)} instances so far")

            except Exception as e:
                logger.error(f"Skipping project {project_id} due to error: {e}")
                continue

    if not instances:
        logger.warning("No instances found across all projects")
        return pd.DataFrame(), TABLE_NAME

    df = pd.DataFrame(instances)

    #Add ingestion timestamp
    ingested_at = datetime.now(timezone.utc)
    df["ingested_at"] = ingested_at

    logger.info(f"Fetched {len(df)} instances")

    return df, TABLE_NAME