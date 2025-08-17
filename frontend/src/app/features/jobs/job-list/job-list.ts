import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatTableModule } from '@angular/material/table';
import { MatIconModule } from '@angular/material/icon';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
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
    MatDialogModule
  ],
  templateUrl: './job-list.html',
  styleUrl: './job-list.scss'
})
export class JobListComponent implements OnInit {
  jobs: Job[] = [];
  displayedColumns = ['title', 'team', 'status', 'actions'];
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
    this.showCreateJobButton = user?.role === 'admin' || user?.role === 'hr' || user?.role === 'manager';
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

  deleteJob(job: Job): void {
    if (confirm(`Are you sure you want to delete "${job.title}"?`)) {
      this.apiService.deleteJob(job.id).subscribe({
        next: () => {
          this.jobs = this.jobs.filter(j => j.id !== job.id);
          this.snackBar.open('Job deleted successfully', 'Close', { duration: 3000 });
        },
        error: (error) => {
          this.snackBar.open('Failed to delete job', 'Close', { duration: 3000 });
        }
      });
    }
  }

  triggerMatching(job: Job): void {
    // Inform user what this does
    if (confirm(`Trigger AI matching for "${job.title}"?\n\nThis will analyze employee profiles and find the best candidates for this position based on their skills and experience.`)) {
      this.apiService.triggerMatching(job.id).subscribe({
        next: () => {
          this.snackBar.open('Matching completed! Reviewing candidates...', 'Close', { duration: 3000 });
          // Navigate to job matches page where HR can review and invite candidates
          this.router.navigate(['/jobs', job.id, 'matches']);
        },
        error: (error) => {
          console.error('Error triggering matching:', error);
          this.snackBar.open('Failed to trigger matching', 'Close', { duration: 3000 });
        }
      });
    }
  }

  canManageJob(job: Job): boolean {
    const user = this.authService.getCurrentUser();
    return user?.role === 'admin' || user?.role === 'hr' || user?.id === job.manager_id;
  }

  canTriggerMatching(): boolean {
    const user = this.authService.getCurrentUser();
    return user?.role === 'admin' || user?.role === 'hr';
  }
}
