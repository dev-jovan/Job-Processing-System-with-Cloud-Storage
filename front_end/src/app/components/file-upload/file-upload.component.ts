import { Component, EventEmitter, Output } from '@angular/core';
import { JobService } from '../../services/job.service';  // Import JobService

@Component({
  selector: 'app-file-upload',
  standalone: true,
  templateUrl: './file-upload.component.html',
  styleUrls: ['./file-upload.component.css']
})
export class FileUploadComponent {
  @Output() fileUploaded = new EventEmitter<string>();
  selectedFile: File | null = null;
  uploading = false;

  constructor(private jobService: JobService) {}  // Inject JobService here

  onFileChange(event: any) {
    this.selectedFile = event.target.files[0];
  }

  uploadFile() {
    if (!this.selectedFile) return;
    this.uploading = true;
    this.jobService.upload(this.selectedFile).subscribe({
      next: (res: any) => {
        this.fileUploaded.emit(res.file_id);
        alert('Upload successful!');
      },
      error: () => alert('Upload failed. Please try again.'),
      complete: () => this.uploading = false
    });
  }
}
