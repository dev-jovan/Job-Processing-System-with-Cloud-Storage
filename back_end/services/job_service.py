from sqlalchemy.orm import Session
from models.job import Job
from models.user import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class JobService:
    def __init__(self, db: Session):
        self.db = db

    def create_job(self, file_id: str, user_id: int):
        job = Job(file_id=file_id, status="Pending", user_id=user_id)
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def get_job_by_file_id(self, file_id: str):
        return self.db.query(Job).filter(Job.file_id == file_id).first()
    
    def get_job_by_job_id(self, job_id: int):
        return self.db.query(Job).filter(Job.id == job_id).first()

    def update_job_status(self, file_id: str, status: str):
        job = self.get_job_by_file_id(file_id)
        if job:
            job.status = status
            self.db.commit()

    def update_job_result(self, file_id: str, result_url: str):
        job = self.get_job_by_file_id(file_id)
        if job:
            job.result_url = result_url
            self.db.commit()
    
    def update_job_name(self, file_id: str, job_name: str):
        job = self.get_job_by_file_id(file_id)
        if job:
            job.job_name = job_name
            self.db.commit()

    def get_all_jobs(self):
        return self.db.query(Job).order_by(Job.id).all()
    
    def delete_job(self, job_id: int):
        job = self.get_job_by_job_id(job_id)
        if job:
            self.db.delete(job)
            self.db.commit()

    def get_jobs_by_user(self, userid: int):
        return self.db.query(Job).filter(Job.user_id == userid).all()
    
    def get_user_by_username(self, username: int):
        return self.db.query(User).filter(User.username == username).first()

    def create_user(self, username: str, hashed_password: str):
        user = User(username=username, hashed_password=hashed_password)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def verify_password(self, plain_password: str, hashed_password: str):
        return pwd_context.verify(plain_password, hashed_password)

    def authenticate_user(self, username: str, password: str):
        user = self.get_user_by_username(username)
        if not user or not self.verify_password(password, user.hashed_password):
            return None
        return user
