from googleapiclient.discovery import build
from ingestion.utils.logging import get_logger
import ingestion.config as config

#Initialize Logger
logger = get_logger()

def get_active_gcp_projects(config):
    #Fetch list of GCP projects accessible by the service account.

    #Allow for a light weight DEBUG run
    if config.DEBUG == "True":
        projects = ["***-dev*****"]
        logger.info(f"Debug mode enabled, using only {projects}")
        return projects
    else:

        try:
            crm = build("cloudresourcemanager", "v1")

            logger.info("Querying GCP Resource Manager API for projects")
            request = crm.projects().list()

            projects = []

            while request is not None:
                response = request.execute()

                for project in response.get("projects", []):
                    if project["lifecycleState"] == "ACTIVE":
                        projects.append(project["projectId"])

                request = crm.projects().list_next(
                    previous_request=request,
                    previous_response=response
                )

            if projects:
                logger.info(f"Discovered {len(projects)} projects from GCP")
                return projects
            else:
                projects = ["***-dev****"]
                logger.warning(f"Fall back to {projects} since no GCP projects discovered")
                return projects

        except Exception as e:
            logger.warning(f"Failed to fetch projects from GCP: {e}")

    #Fallback to env config
    if config.GCP_PROJECT_LIST:
        return [p.strip() for p in config.GCP_PROJECT_LIST.split(",")]

    return [config.GCP_PROJECT_ID]

