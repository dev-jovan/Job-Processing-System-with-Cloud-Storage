import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FileUploadComponent } from '../file-upload/file-upload.component';
import { JobSubmitComponent } from '../job-submit/job-submit.component';
import { JobStatusComponent } from '../job-status/job-status.component';
import { Router } from '@angular/router';
import { AuthService } from '../../auth/auth.service';

@Component({
    selector: 'app-dashboard',
    standalone: true,
    imports: [CommonModule, FileUploadComponent, JobSubmitComponent, JobStatusComponent ],
    templateUrl: './dashboard.component.html',
    styleUrls: ['./dashboard.component.css']
  })
  export class DashboardComponent implements OnInit {
    fileId = '';
    username: string | null = null;
  
    constructor(private authService: AuthService, private router: Router) {}
  
    ngOnInit() {
      this.username = localStorage.getItem('username');
      if (!this.authService.isLoggedIn()) {
        this.router.navigate(['/login']);
      }
    }
  
    onFileUploaded(fileId: string) {
      this.fileId = fileId;
    }
  
    logout() {
      this.authService.logout();
      this.router.navigate(['/login']);
    }
  }