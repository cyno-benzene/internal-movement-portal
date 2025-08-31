import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatTableModule } from '@angular/material/table';
import { MatIconModule } from '@angular/material/icon';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatRippleModule } from '@angular/material/core';
import { ApiService } from '../../../core/services/api';
import { AuthService } from '../../../core/services/auth';
import { Job } from '../../../core/models/job.model';

@Component({
  selector: 'app-job-list',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    MatCardModule,
    MatButtonModule,
    MatTableModule,
    MatIconModule,
    MatSnackBarModule,
    MatDialogModule,
    MatRippleModule
  ],
  templateUrl: './job-list.html',
  styleUrl: './job-list.scss'
})
export class JobListComponent implements OnInit {
  jobs: Job[] = [];
  displayedColumns = ['title', 'team', 'status'];
  showCreateJobButton = false;

  constructor(
    private apiService: ApiService,
    private authService: AuthService,
    private snackBar: MatSnackBar,
    private dialog: MatDialog,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.loadJobs();
    const user = this.authService.getCurrentUser();
    // Only admin and manager users can create jobs, not HR
    this.showCreateJobButton = user?.role === 'admin' || user?.role === 'manager';
  }

  loadJobs(): void {
    this.apiService.getJobs().subscribe({
      next: (jobs) => {
        const user = this.authService.getCurrentUser();
        
        // Filter jobs based on user role
        if (user?.role === 'manager') {
          // Managers only see jobs they created
          this.jobs = jobs.filter(job => job.manager_id === user.id);
        } else {
          // HR and Admin see all jobs
          this.jobs = jobs;
        }
      },
      error: (error) => {
        console.error('Error loading jobs:', error);
        this.snackBar.open('Failed to load jobs', 'Close', { duration: 3000 });
      }
    });
  }

  viewJob(job: Job): void {
    // Navigate to job details page
    this.router.navigate(['/jobs', job.id]);
  }
}
