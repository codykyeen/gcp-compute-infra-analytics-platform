
from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.bash import BashOperator

default_args = {
    "owner": "cody",
    "retries": 1,
    "retry_delay": timedelta(minutes=5)
}

with DAG(
    dag_id="gcp_compute_pipeline_cloud_run",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    #schedule="@hourly",
    catchup=False,
    default_args=default_args
) as dag:

    run_pipeline = BashOperator(
        task_id="run_cloud_run_job",
        bash_command="""
        echo "Triggering Cloud Run job: gcp-compute-resource-reporting"
        date
        export GOOGLE_APPLICATION_CREDENTIALS=/opt/airflow/credentials/service-account.json &&
        gcloud auth activate-service-account --key-file=$GOOGLE_APPLICATION_CREDENTIALS &&
        gcloud config set project <gcp_project> &&
        gcloud run jobs execute gcp-compute-resource-reporting \
          --region <region> \
          --project <gcp_project> \
          --wait
        """
    )


