from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
import os
import uuid
import boto3
from dotenv import load_dotenv
import logging

# Custom imports
from services.job_service import JobService
from models.job import Job
from models.user import User
from utils.auth import get_current_user, router as auth_router

# Load environment variables
load_dotenv()

# FastAPI app initialization
app = FastAPI()

app.include_router(auth_router) 
# Database configuration (PostgreSQL)
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# MinIO configuration
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
s3 = boto3.client('s3',
                  endpoint_url=MINIO_ENDPOINT,
                  aws_access_key_id=MINIO_ACCESS_KEY,
                  aws_secret_access_key=MINIO_SECRET_KEY)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # Allow your Angular frontend
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class SignupRequest(BaseModel):
    username: str
    password: str

@app.post("/signup")
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == request.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_password = pwd_context.hash(request.password)
    user = User(username=request.username, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    return {"message": "User created successfully"}

# Pydantic model for job submission
class SubmitJobRequest(BaseModel):
    file_id: str
    job_name: str
# Route to handle file upload
@app.post("/upload/")
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    file_id = str(uuid.uuid4())  # Generate a unique file ID
    try:
        # Upload file to MinIO
        s3.upload_fileobj(file.file, 'uploads', f"{file_id}.csv")

        # Save job metadata in PostgreSQL
        job_service = JobService(db)
        job_service.create_job(file_id, user_id=user.id)
        return {"file_id": file_id, "status": "Uploaded"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

# Route to handle job submission
@app.post("/submit/")
async def submit_job(request: SubmitJobRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    file_id = request.file_id  # Get file_id from the request body
    job_name = request.job_name # Get job_name from the request body
    job_service = JobService(db)
    job = job_service.get_job_by_file_id(file_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Update job status to 'Running'
    job_service.update_job_status(file_id, "Running")

    # Update job name
    job_service.update_job_name(file_id, job_name)
    
    return {"status": "Job submitted successfully"}

class AirflowUpdateRequest(BaseModel):
    file_id: str
    status: str  # e.g., "Completed" or "Failed"
    result_url: str

@app.post("/airflow/update-status/")
async def airflow_update_status(request: AirflowUpdateRequest, db: Session = Depends(get_db)):
    job_service = JobService(db)
    job = job_service.get_job_by_id(request.file_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    job_service.update_job_status(request.file_id, request.status)
    job_service.update_job_result(request.file_id, request.result_url)
    return {"message": "Job updated successfully"}

# Route to retrieve all jobs
@app.get("/jobs/")
async def get_jobs(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    job_service = JobService(db)
    jobs = job_service.get_jobs_by_user(user.id)
    return {"jobs": jobs}

# Route to delete job
@app.delete("/jobs/{job_id}")
async def delete_job(job_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    job_service = JobService(db)
    job = job_service.get_job_by_job_id(job_id)
    file_id = job.file_id

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Optionally delete file from MinIO
    try:
        s3.delete_object(Bucket="uploads", Key=f"{file_id}.csv")
    except Exception as e:
        logging.warning(f"Could not delete file from MinIO: {str(e)}")

    job_service.delete_job(job_id)
    return {"message": "Job deleted successfully"}

# Route to retry job
@app.patch("/jobs/{file_id}/retry")
async def retry_job(file_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    job_service = JobService(db)
    job = job_service.get_job_by_job_id(file_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Retry logic: reset status and clear result
    job_service.update_job_status(file_id, "running")
    job_service.update_job_result(file_id, "")
    return {"message": "Job retry initiated"}
