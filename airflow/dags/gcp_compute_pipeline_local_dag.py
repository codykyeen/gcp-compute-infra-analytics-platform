from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    "owner": "cody",
    "retries": 1,
    "retry_delay": timedelta(minutes=5)
}

with DAG(
    dag_id="gcp_compute_pipeline",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    #schedule="@hourly",
    catchup=False,
    default_args=default_args,
) as dag:

    ingest_instances = BashOperator(
        task_id="ingest_instances",
        bash_command="""
        cd /opt/airflow &&
        export PYTHONPATH=/opt/airflow &&
        export DATA_SOURCE=gcp_instances_pull &&
        export GOOGLE_APPLICATION_CREDENTIALS=/opt/airflow/credentials/service-account.json &&
        export DEBUG=false &&
        python -m ingestion.data_ingest
        """
    )

    ingest_disks = BashOperator(
        task_id="ingest_disks",
        bash_command="""
        cd /opt/airflow &&
        export PYTHONPATH=/opt/airflow &&
        export DATA_SOURCE=gcp_disks_pull &&
        export GOOGLE_APPLICATION_CREDENTIALS=/opt/airflow/credentials/service-account.json &&
        export DEBUG=false &&
        python -m ingestion.data_ingest
        """
    )

    ingest_snapshots = BashOperator(
        task_id="ingest_snapshots",
        bash_command="""
        cd /opt/airflow &&
        export PYTHONPATH=/opt/airflow &&
        export DATA_SOURCE=gcp_snapshots_pull &&
        export GOOGLE_APPLICATION_CREDENTIALS=/opt/airflow/credentials/service-account.json &&
        export DEBUG=false &&
        python -m ingestion.data_ingest
        """
    )

    run_dbt = BashOperator(
        task_id="run_dbt",
        bash_command="""
        cd /opt/airflow &&
        export PYTHONPATH=/opt/airflow &&
        export DATA_SOURCE=gcp_instances_pull &&
        export GOOGLE_APPLICATION_CREDENTIALS=/opt/airflow/credentials/service-account.json &&
        export DEBUG=false &&
        dbt run --project-dir dbt/resource_models --profiles-dir dbt_profiles
        """
    )

    # Dependencies (parallel ingestion then dbt)
    [ingest_instances, ingest_disks, ingest_snapshots] >> run_dbt
