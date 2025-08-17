import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { ApiService } from '../../../core/services/api';
import { AuthService } from '../../../core/services/auth';
import { Job } from '../../../core/models/job.model';

@Component({
  selector: 'app-job-details',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatChipsModule,
    MatSnackBarModule
  ],
  templateUrl: './job-details.html',
  styleUrl: './job-details.scss'
})
export class JobDetailsComponent implements OnInit {
  job: Job | null = null;
  isLoading = true;
  currentUser: any;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private apiService: ApiService,
    private authService: AuthService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.currentUser = this.authService.getCurrentUser();
    const jobId = this.route.snapshot.paramMap.get('id');
    if (jobId) {
      this.loadJob(jobId);
    }
  }

  private loadJob(jobId: string): void {
    this.apiService.getJob(jobId).subscribe({
      next: (job) => {
        this.job = job;
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error loading job:', error);
        this.snackBar.open('Failed to load job details', 'Close', { duration: 3000 });
        this.router.navigate(['/jobs']);
      }
    });
  }

  canManageJob(): boolean {
    return this.currentUser?.role === 'admin' || 
           this.currentUser?.role === 'hr' || 
           this.currentUser?.id === this.job?.manager_id;
  }

  editJob(): void {
    if (this.job) {
      this.router.navigate(['/jobs/edit', this.job.id]);
    }
  }

  viewMatches(): void {
    if (this.job) {
      this.router.navigate(['/jobs', this.job.id, 'matches']);
    }
  }

  goBack(): void {
    this.router.navigate(['/jobs']);
  }
}
