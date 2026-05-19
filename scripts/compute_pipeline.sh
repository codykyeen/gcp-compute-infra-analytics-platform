#!/bin/bash

echo "Starting full ingestion + dbt pipeline"

set -e

# Detect environment
if [ -d "/app" ]; then
    cd /app
else
    cd "$(dirname "$0")/.."
fi

export DEBUG=false

for source in gcp_instances_pull gcp_disks_pull gcp_snapshots_pull
do
  echo "-----------------------"
  echo "Running python script $source.py"

  export DATA_SOURCE=$source
  python -m ingestion.data_ingest
  echo "Completed ingesiton from $source.py"
  date
done

echo "-----------------------"
echo "Running dbt Models"
date

cd dbt/resource_models
dbt run --profiles-dir ../../dbt_profiles

echo "Pipeline completed successfully"
date

