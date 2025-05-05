# models/job.py

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(String, index=True)
    status = Column(String, index=True)
    result_url = Column(String, nullable=True)
    job_name = Column(String, nullable=True)
    user_id = Column(Integer, nullable=True)