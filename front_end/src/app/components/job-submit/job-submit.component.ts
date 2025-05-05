import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { JobService } from '../../services/job.service'; 

@Component({
  selector: 'app-job-submit',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './job-submit.component.html',
  styleUrls: ['./job-submit.component.css']
})
export class JobSubmitComponent {
  @Input() fileId: string = '';
  jobName: string = '';
  submitting = false;

  constructor(private jobService: JobService) {} 

  submitJob() {
    if (!this.fileId || !this.jobName.trim()) return;

    this.submitting = true;
    this.jobService.submitJob(this.fileId, this.jobName).subscribe({
      next: () => {
        alert('Job submitted successfully!');
        this.jobName = '';
      },
      error: () => alert('Failed to submit job.'),
      complete: () => this.submitting = false
    });
  }
}
