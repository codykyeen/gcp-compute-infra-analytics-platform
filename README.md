This three day learning sprint was designed to familiarize myself with a modern data stack while solving a real world business problem.

See: https://github.com/codykyeen/gcp-compute-infra-analytics-platform/blob/main/Executive%20Summary.pdf

# 🚀 GCP Compute Resource Pipeline

## 📌 Overview

This project is a fully automated data pipeline that:

- Collects GCP compute resource data (instances, disks, snapshots)
- Loads raw data into BigQuery
- Transforms data using dbt
- Orchestrates execution via Airflow
- Executes workloads via Cloud Run
- Deploys via Cloud Build (CI/CD)

The Cloud Run is scheduled to run hourly outside of this workflow (stateless exeuciton)
See details: https://console.cloud.google.com/cloudscheduler?project=<gcp_project>

Dashboard Link: https://datastudio.google.com/reporting/<report_id>/page/<page_id>

Screenshots: https://github.com/codykyeen/gcp-compute-infra-analytics-platform/tree/main/dashboard

---

## 🏗️ Architecture

### Runtime Flow

Airflow (Docker)
    ↓
Cloud Run Job
    ↓
Ingestion (Python)
    ↓
Raw BigQuery Tables
    ↓
dbt Transformations
    ↓
Analytics Tables

---

### Deployment Flow (CI/CD)

GitHub
    ↓
Cloud Build
    ↓
Artifact Registry (Docker Image)
    ↓
Cloud Run Job (updated automatically)

---

## 📁 Repository Structure

```
gcp_compute_pipeline/
│
├── ingestion/
├── dbt/
├── airflow/
│   └── dags/
│
├── scripts/
│   └── run_pipeline.sh
│
├── Dockerfile
├── Dockerfile.airflow
├── docker-compose.yml
├── cloudbuild.yaml
│
├── requirements.txt
├── requirements-airflow.txt
│
├── credentials/       # local only (ignored in git)
├── logs/              # local only
│
└── README.md
```

---

## 🧰 Prerequisites

- Docker + docker-compose
- gcloud CLI (authenticated)
- GCP project with:
  - Cloud Run
  - BigQuery
  - Artifact Registry
  - Cloud Build enabled

---

## 🔧 Local Setup (Airflow)

### Start Airflow

```bash
docker-compose up airflow-init
docker-compose up -d
```

---

### Access UI

```
http://localhost:8080/
```

---

### Login

```
username: admin
password: admin
```

---

## ▶️ Manually Running the Pipeline

### ✅ Option 1 — Through Airflow

- Open Airflow UI
- Trigger DAG:
  ```
  gcp_compute_pipeline_cloud_run
  ```

---

### ✅ Option 2 — Manual (Cloud Run)

```bash
gcloud run jobs execute gcp-compute-resource-reporting \
  --region <region> \
  --project <gcp_project>
  --wait
```

---

## 🔄 Deploying Updates (CI/CD)

### Manual Deploy

```bash
gcloud builds submit --config cloudbuild.yaml .
```

---

### What this does

- Builds Docker image
- Pushes to Artifact Registry
- Updates Cloud Run job

---

## 🔐 Credentials

Place your service account key here:

```
credentials/service-account.json
```

⚠️ Do NOT commit credentials.

---

## ⚙️ Scheduling (rememeber to disable Cloud Scheduler)

Update DAG:

```python
schedule="@hourly"
```

Options:

- `None` → manual only
- `@hourly` → hourly runs
- `@daily` → daily runs

---

## 📊 Data Flow

1. Airflow triggers Cloud Run job
2. Cloud Run executes ingestion + dbt
3. Data lands in BigQuery
4. dbt produces analytics tables

---

## dbt Details
See: https://github.com/codykyeen/gcp-compute-infra-analytics-platform/blob/main/dbt/resource_models/README.md

---

## 🧪 Development Workflow

1. Update code (ingestion, dbt, scripts)
2. Deploy:

```bash
gcloud builds submit --config cloudbuild.yaml .
```

3. Run pipeline via Airflow

---

## 💰 Cost Considerations

- Airflow: free (runs locally)
- Cloud Run: per execution
- BigQuery: query + storage costs

---

## 🔒 Security

- Airflow runs locally
- Cloud Run uses service account
- Cloud Build uses controlled IAM roles
- Credentials excluded from Git

---

## ✅ Key Capabilities

- Fully automated pipeline
- Containerized orchestration (Airflow)
- Serverless execution (Cloud Run)
- CI/CD via Cloud Build
- dbt-based transformation layer

---

## 🚀 Next Steps

- Add alerts
- Optimize queries/models
- Move secrets to Secret Manager
- Automate cleanup of raw data imports after a set period of time
