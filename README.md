# Digi-Sapiens Job Processor

## Project Overview
This project is a **Job Processor** that involves handling jobs through a **FastAPI** backend, storing files in **MinIO**, processing them using **Airflow**, and displaying the results in a **Frontend** (Angular app). The job status and other related information are managed throughout the process, and users can submit jobs, view job statuses, and download the processed files.

---

## Technologies Used
- **Backend**: FastAPI (Python)
- **Frontend**: Angular
- **Orchestration**: Apache Airflow
- **Storage**: MinIO (S3-compatible object storage)
- **Database**: PostgreSQL
- **Containerization**: Docker and Docker Compose

---

## Getting Started

These instructions will help you set up and run the project on your local machine for development and testing purposes.

### Prerequisites
- Docker and Docker Compose must be installed.
  - [Install Docker](https://docs.docker.com/get-docker/)
  - [Install Docker Compose](https://docs.docker.com/compose/install/)
- Python 3.x (for FastAPI backend)
- Node.js and npm (for Angular frontend)

---

## Project Structure

```plaintext
/
├── backend/             # FastAPI Backend
│   ├── Dockerfile       # Dockerfile for backend container
│   ├── requirements.txt # Python dependencies for backend
│   └── app/             # FastAPI app code
├── frontend/            # Angular Frontend
│   ├── Dockerfile       # Dockerfile for frontend container
│   └── src/             # Angular app code
├── airflow/             # Airflow setup
│   ├── Dockerfile       # Dockerfile for Airflow container
│   ├── dags/            # Airflow DAGs
│   └── requirements.txt # Python dependencies for Airflow
├── docker-compose.yml   # Docker Compose file to run all containers
├── .env                 # Environment variables for Docker Compose
└── README.md            # Project documentation (this file)

```

## Project Initialization Guide

Follow these steps to initialize and run the project on your local environment.

### Step 1: Clone the Repository

```bash
git clone <repository_url>
cd <project_directory>
```
## Step 2: Install Docker and Docker Compose

Follow the Docker installation guide for your OS.

- [Install Docker](https://docs.docker.com/get-docker/)
- [Install Docker Compose](https://docs.docker.com/compose/install/)

---

## Step 3: Configure Environment Variables

Create a `.env` file in the root directory to store sensitive information like access keys, database connections, etc. Here's a sample configuration for `.env`:

Airflow Environment
```airflow env
# Airflow Configuration
MINIO_ROOT_USER="minio_access_key"
MINIO_ROOT_PASSWORD="minio_secret_key"
MINIO_BUCKET_NAME="processed"
```

Backend Environment
```backend env
# Database Connection
DATABASE_URL=postgresql://postgres:root@localhost:5432/test

# MinIO Configuration
MINIO_ENDPOINT=http://localhost:9000
MINIO_ACCESS_KEY= "minio_access_key"
MINIO_SECRET_KEY= "minio_secret_key"
```
## Step 4: Build and Run the Containers

Run the following command to build and start all services (Backend, Frontend, MinIO, Airflow, PostgreSQL):

```bash
docker-compose up --build
```
This will:

- Build the Docker images for the Frontend, Backend, Airflow, PostgreSQL, and MinIO services.

- Start all the services and link them together.


## Step 5: Access the Services

After the containers are up and running, you can access the following services:

- **Frontend (Angular)**: [http://localhost:4200](http://localhost:4200)
- **Backend (FastAPI)**: [http://localhost:8000](http://localhost:8000)
- **Airflow Web UI**: [http://localhost:8080](http://localhost:8080)
- **MinIO UI**: [http://localhost:9000](http://localhost:9000)

---
## Run Project with out Docker
### Step 1: Clone the Repository

```bash
git clone <repository_url>
cd <project_directory>
```
### Step2: Run Backend Service
 - cd back_end and pip install -r requirements.txt.
 - run cmd uvicorn app.main:app -- host 0.0.0.0 --port 8000
### Step3: Run Frontend Service
 - cd front_end and run npm install.
 - run ng serve --open
### Step4: Run Airflow Service
 - cd airflow and run pip install -r requirements.txt
 - run airflow standalone.
 - On Airflow UI, we can set postgres connection.
 - On Airflow UI, we can set dag setup.
 - On Airflow UI, we can trigger dag.
### Step5: Run Minio Service.
https://www.blackslate.io/articles/how-to-install-and-configure-minio
## Project Features

### Frontend (Angular)
- **Job Status Dashboard**: Displays the status of all submitted jobs.
- **Job Submission**: Allows users to upload files and submit jobs to the backend for processing.

### Backend (FastAPI)
- **File Upload**: Accepts file uploads and stores them in MinIO.
- **Job Management**: Handles job submissions, status updates, and fetching job results.

### Airflow
- **Job Processing**: Executes tasks related to job processing, such as file transformation and uploading the processed data to MinIO.

### MinIO
- **Object Storage**: Stores uploaded and processed files for jobs.