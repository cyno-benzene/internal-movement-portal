import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatGridListModule } from '@angular/material/grid-list';
import { MatTableModule } from '@angular/material/table';
import { MatTabsModule } from '@angular/material/tabs';
import { MatChipsModule } from '@angular/material/chips';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { ApiService } from '../../../core/services/api';
import { AuthService } from '../../../core/services/auth';
import { InvitationService } from '../../../core/services/invitation';
import { Job, Invitation } from '../../../core/models/job.model';

@Component({
  selector: 'app-manager-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatGridListModule,
    MatTableModule,
    MatTabsModule,
    MatSnackBarModule
  ],
  templateUrl: './manager-dashboard.html',
  styleUrls: ['./manager-dashboard.scss']
})
export class ManagerDashboardComponent implements OnInit {
  myJobs: Job[] = [];
  sentInvitations: Invitation[] = [];
  
  jobStats = {
    totalJobs: 0,
    activeJobs: 0,
    closedJobs: 0,
    draftJobs: 0
  };
  
  invitationStats = {
    totalInvitations: 0,
    pending: 0,
    accepted: 0,
    declined: 0
  };
  isLoading = true;

  invitationColumns = ['employee_name', 'job_title', 'sent_date', 'status', 'actions'];

  constructor(
    private apiService: ApiService,
    private authService: AuthService,
    private invitationService: InvitationService,
    private snackBar: MatSnackBar,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.loadDashboardData();
  }

  private async loadDashboardData(): Promise<void> {
    try {
      this.isLoading = true;
      
      // Load jobs I manage
      await this.loadMyJobs();
      
      // Calculate job statistics
      this.calculateJobStats();
      
    } catch (error) {
      console.error('Error loading dashboard data:', error);
      this.showError('Failed to load dashboard data');
    } finally {
      this.isLoading = false;
    }
  }

  private async loadMyJobs(): Promise<void> {
    try {
      return new Promise((resolve, reject) => {
        this.apiService.getJobs().subscribe({
          next: (jobs) => {
            // Filter jobs where current user is the manager
            this.myJobs = jobs.filter(job => job.manager_id === this.authService.getCurrentUser()?.id);
            console.log('Loaded my jobs:', this.myJobs); // Debug log
            resolve();
          },
          error: (error) => {
            console.error('Error loading jobs:', error);
            this.myJobs = [];
            reject(error);
          }
        });
      });
    } catch (error) {
      console.error('Error loading jobs:', error);
      this.myJobs = [];
      throw error;
    }
  }

  private async loadSentInvitations(): Promise<void> {
    // Managers don't send invitations anymore - HR does
    // This method is kept for backwards compatibility but does nothing
    this.sentInvitations = [];
  }

  private calculateJobStats(): void {
    // Calculate job-related statistics for managers
    const stats = this.myJobs.reduce((acc, job) => {
      acc.totalJobs++;
      switch (job.status) {
        case 'active':
          acc.activeJobs++;
          break;
        case 'closed':
          acc.closedJobs++;
          break;
        case 'draft':
          acc.draftJobs++;
          break;
      }
      return acc;
    }, {
      totalJobs: 0,
      activeJobs: 0,
      closedJobs: 0,
      draftJobs: 0
    });

    // Update job statistics
    this.jobStats = stats;
  }

  private calculateInvitationStats(): void {
    const stats = this.sentInvitations.reduce((acc, invitation) => {
      acc.totalInvitations++;
      switch (invitation.status) {
        case 'pending':
          acc.pending++;
          break;
        case 'accepted':
          acc.accepted++;
          break;
        case 'declined':
          acc.declined++;
          break;
      }
      return acc;
    }, {
      totalInvitations: 0,
      pending: 0,
      accepted: 0,
      declined: 0
    });

    this.invitationStats = stats;
  }

  // Method to discover candidates for a job
  async discoverCandidates(jobId: string): Promise<void> {
    try {
      this.apiService.discoverCandidates(jobId).subscribe({
        next: (candidates) => {
          this.showSuccess(`Found ${candidates.length} potential candidates`);
          // Navigate to job discovery page or show candidates
        },
        error: (error) => {
          console.error('Error discovering candidates:', error);
          this.showError('Failed to discover candidates');
        }
      });
    } catch (error) {
      console.error('Error discovering candidates:', error);
      this.showError('Failed to discover candidates');
    }
  }

  getStatusClass(status: string): string {
    return status.toLowerCase().replace('_', '-');
  }

  getStatusIcon(status: string): string {
    switch (status) {
      case 'pending': return 'schedule';
      case 'accepted': return 'check_circle';
      case 'declined': return 'cancel';
      default: return 'help';
    }
  }

  async viewInvitationDetails(invitationId: string): Promise<void> {
    try {
      // Navigate to invitation details page
      this.router.navigate(['/invitations', invitationId]);
    } catch (error) {
      console.error('Error navigating to invitation details:', error);
      this.showError('Failed to view invitation details');
    }
  }

  async withdrawInvitation(invitationId: string): Promise<void> {
    try {
      // Call API to withdraw invitation
      // For now, just show a message and remove from local array
      this.sentInvitations = this.sentInvitations.filter(inv => inv.id !== invitationId);
      this.calculateInvitationStats();
      this.showSuccess('Invitation withdrawn successfully');
    } catch (error) {
      console.error('Error withdrawing invitation:', error);
      this.showError('Failed to withdraw invitation');
    }
  }

  private showSuccess(message: string): void {
    this.snackBar.open(message, 'Close', {
      duration: 3000,
      panelClass: ['success-snackbar']
    });
  }

  private showError(message: string): void {
    this.snackBar.open(message, 'Close', {
      duration: 5000,
      panelClass: ['error-snackbar']
    });
  }
}
