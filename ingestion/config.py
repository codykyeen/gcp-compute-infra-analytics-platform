#Import Operating System
import os

#Define Data Location Variables
DATA_PROJECT_ID = os.getenv("DATA_GCP_PROJECT", "***-prod*****")
DATASET_NAME = os.getenv("BQ_DATASET", "stl_resource_log")


#Define BQ Mode
WRITE_MODE = os.getenv("WRITE_MODE", "append")

#Define Data Source (i.e. which data to ingest)
DATA_SOURCE = os.getenv("DATA_SOURCE", "sample")

#Create Debug (runs only using ***-dev**** project)
DEBUG = os.getenv("DEBUG", "True")

#Define GCP Project List
##Array of all GCP Projects
GCP_PROJECT_LIST = os.getenv("GCP_PROJECT_LIST", "")
##Current GCP Project
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "")

#Define Log File Information
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, "logs")