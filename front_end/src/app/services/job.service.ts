import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { JobStatus } from '../models/job-status.model';

@Injectable({ providedIn: 'root' })
export class JobService {
  private baseUrl = 'http://localhost:8000';

  constructor(private http: HttpClient) {}

  upload(file: File): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post(`${this.baseUrl}/upload`, formData);
  }

  submitJob(fileId: string, jobName: string): Observable<any> {
    const body = { file_id: fileId, job_name: jobName };
    return this.http.post(`${this.baseUrl}/submit`, body);
  }

  getJobs(): Observable<{ jobs: JobStatus[] }> {
    return this.http.get<{ jobs: JobStatus[] }>(`${this.baseUrl}/jobs`);
  }

  // ✅ NEW: Get a single job by ID
  getJobById(jobId: number): Observable<JobStatus> {
    return this.http.get<JobStatus>(`${this.baseUrl}/jobs/${jobId}`);
  }

  // ✅ NEW: Delete a job by ID
  deleteJob(jobId: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}/jobs/${jobId}`);
  }
}
