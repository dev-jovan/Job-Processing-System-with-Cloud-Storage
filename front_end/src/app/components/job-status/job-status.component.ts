import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { JobService } from '../../services/job.service';
import { JobStatus } from '../../models/job-status.model';
import { interval, Subscription } from 'rxjs';

@Component({
  selector: 'app-job-status',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './job-status.component.html',
  styleUrls: ['./job-status.component.css']
})
export class JobStatusComponent implements OnInit, OnDestroy {
  jobs: JobStatus[] = [];
  refreshSub!: Subscription;
  isLoading: boolean = false;  // Track loading state
  errorMessage: string = '';   // For error messages

  constructor(private jobService: JobService) {}

  ngOnInit() {
    this.loadJobs();  // Initial load of jobs
    this.refreshSub = interval(10000).subscribe(() => this.loadJobs());  // Auto-refresh every 10 seconds
  }

  ngOnDestroy() {
    // Ensure we unsubscribe from the interval when the component is destroyed
    this.refreshSub?.unsubscribe();
  }

  // Improved loadJobs with error handling and loading state
  loadJobs() {
    this.isLoading = true;  // Set loading state before making the API request
    this.errorMessage = '';  // Clear previous error message if any

    this.jobService.getJobs().subscribe({
      next: (data: any) => {
        // Ensure the data is an array before assigning
        if (Array.isArray(data?.jobs)) {
          this.jobs = data?.jobs??[];
        } else {
          this.errorMessage = 'Error: Received data is not in expected format';
        }
      },
      error: (err) => {
        console.error('Error fetching jobs', err);
        this.errorMessage = 'Failed to load jobs. Please try again later.';  // Show error message if API call fails
      },
      complete: () => {
        this.isLoading = false;  // Stop loading once the request completes
      }
    });
  }

  refreshJob(jobId: number) {
    this.jobService.getJobById(jobId).subscribe({
      next: (updatedJob: JobStatus) => {
        const index = this.jobs.findIndex(job => job.id === jobId);
        if (index !== -1) this.jobs[index] = updatedJob;
      },
      error: (err) => {
        console.error(`Failed to refresh job ${jobId}`, err);
        alert(`Failed to refresh job ${jobId}`);
      }
    });
  }

  deleteJob(jobId: number) {
    if (!confirm(`Are you sure you want to delete job #${jobId}?`)) return;

    this.jobService.deleteJob(jobId).subscribe({
      next: () => {
        this.jobs = this.jobs.filter(job => job.id !== jobId);
        alert(`Job #${jobId} deleted`);
      },
      error: (err) => {
        console.error(`Failed to delete job ${jobId}`, err);
        alert(`Failed to delete job ${jobId}`);
      }
    });
  }
}
