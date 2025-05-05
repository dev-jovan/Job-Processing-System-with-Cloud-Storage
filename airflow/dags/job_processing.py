import os
import uuid
import pandas as pd
import requests
from datetime import datetime, timedelta
from minio import Minio
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from dotenv import load_dotenv
from airflow.utils.log.logging_mixin import LoggingMixin

# Load environment variables
load_dotenv()

# Initialize logger
logger = LoggingMixin().log

# DAG default arguments
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime.now() - timedelta(days=1),
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
    "on_failure_callback": None,
}

# DAG definition
dag = DAG(
    dag_id="job_processing_dag",
    description="Process jobs using Airflow, MinIO, and FastAPI",
    default_args=default_args,
    catchup=False,
)

# Environment and constants
TMP_DIR = "/tmp"
MINIO_ENDPOINT = "localhost:9000"
MINIO_ACCESS_KEY = os.getenv("MINIO_ROOT_USER")
MINIO_SECRET_KEY = os.getenv("MINIO_ROOT_PASSWORD")
MINIO_BUCKET = os.getenv("MINIO_BUCKET_NAME")
FASTAPI_URL = "http://localhost:8000"

# Ensure local temp directory exists
os.makedirs(TMP_DIR, exist_ok=True)


# Step 1: Fetch jobs from PostgreSQL
def fetch_jobs_from_db():
    hook = PostgresHook(postgres_conn_id="postgres_conn")
    records = hook.get_records("SELECT id, file_id, status FROM jobs WHERE status = 'Running'")
    logger.info(f"Fetched {len(records)} jobs with status 'Running'")
    return [{"id": r[0], "file_id": r[1], "status": r[2]} for r in records]


# Step 2: Download CSV from MinIO
def download_file_from_minio(file_id: str) -> str:
    client = Minio(MINIO_ENDPOINT, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=False)
    file_path = os.path.join(TMP_DIR, f"{file_id}.csv")
    logger.info(f"Attempting to download file {file_id} from MinIO")
    try:
        client.fget_object("uploads", f"{file_id}.csv", file_path)
        logger.info(f"Downloaded file {file_id} to {file_path}")
    except Exception as e:
        logger.error(f"Error downloading file {file_id}: {e}", exc_info=True)
        raise
    return file_path


# Step 3: Process the CSV file
def process_file(file_path: str) -> str:
    try:
        df = pd.read_csv(file_path)
        df["processed"] = df["data"].apply(lambda x: x.upper())  # Example transformation
        processed_path = os.path.join(TMP_DIR, f"processed_{uuid.uuid4()}.csv")
        df.to_csv(processed_path, index=False)
        logger.info(f"Processed file saved to {processed_path}")
        return processed_path
    except Exception as e:
        logger.error(f"Error processing file {file_path}: {e}", exc_info=True)
        raise


# Step 4: Upload processed file to MinIO
def upload_file_to_minio(file_path: str, file_id: str):
    client = Minio(MINIO_ENDPOINT, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=False)
    
    if not client.bucket_exists(MINIO_BUCKET):
        client.make_bucket(MINIO_BUCKET)
        logger.info(f"Created bucket {MINIO_BUCKET}")

    try:
        with open(file_path, "rb") as f:
            client.put_object(
                bucket_name=MINIO_BUCKET,
                object_name=f"{file_id}_processed.csv",
                data=f,
                length=os.path.getsize(file_path),
                content_type="application/csv",
            )
            logger.info(f"Successfully uploaded {file_id}_processed.csv to MinIO")
    except Exception as e:
        logger.error(f"Error uploading processed file {file_id}: {e}", exc_info=True)
        raise


# Step 5: Notify FastAPI backend
def notify_fastapi(file_id: str, status: str, result_url: str = ""):
    payload = {
        "file_id": file_id,
        "status": status,
        "result_url": result_url
    }
    try:
        res = requests.post(
            f"{FASTAPI_URL}/airflow/update-status/",
            json=payload,
            timeout=10
        )
        res.raise_for_status()
        logger.info(f"FastAPI notified for job {file_id}: {status}")
    except requests.RequestException as e:
        logger.error(f"Failed to notify FastAPI for job {file_id}: {e}", exc_info=True)
        raise


# Step 6: Process a single job
def process_job(job: dict):
    file_id = job["file_id"]
    job_id = job["id"]
    logger.info(f"🔁 Starting job processing: job_id={job_id}, file_id={file_id}")

    try:
        # Start job processing
        notify_fastapi(file_id, "Processing")
        logger.info(f"📨 Notified FastAPI: job_id={job_id} status=Processing")

        # Download, process, and upload the file
        local_file = download_file_from_minio(file_id)
        processed_file = process_file(local_file)
        upload_file_to_minio(processed_file, file_id)

        # Generate result URL after successful upload
        result_url = f"http://minio:9000/{MINIO_BUCKET}/{file_id}_processed.csv"
        
        # Notify FastAPI that the job was completed
        notify_fastapi(file_id, "Completed", result_url)
        logger.info(f"✅ Job completed: job_id={job_id}, result_url={result_url}")

    except Exception as e:
        # In case of an error, set job status to Failed and notify FastAPI
        logger.error(f"❌ Error during job {job_id}: {e}", exc_info=True)
        notify_fastapi(file_id, "Failed")
        logger.info(f"📨 Notified FastAPI: job_id={job_id} status=Failed")
        raise  # Let Airflow mark task as failed


# Airflow tasks
fetch_jobs_task = PythonOperator(
    task_id="fetch_jobs",
    python_callable=fetch_jobs_from_db,
    dag=dag,
)

process_jobs_task = PythonOperator(
    task_id="process_jobs",
    python_callable=lambda: [process_job(job) for job in fetch_jobs_from_db()],
    dag=dag,
)

# Task dependency
fetch_jobs_task >> process_jobs_task
