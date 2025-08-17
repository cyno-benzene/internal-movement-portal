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
import { User } from '../../../core/models/user.model';

@Component({
  selector: 'app-hr-dashboard',
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
    MatChipsModule,
    MatSnackBarModule
  ],
  templateUrl: './hr-dashboard.html',
  styleUrls: ['./hr-dashboard.scss']
})
export class HrDashboardComponent implements OnInit {
  allInvitations: Invitation[] = [];
  allJobs: Job[] = [];
  allUsers: User[] = [];
  
  companyStats = {
    totalEmployees: 0,
    totalJobs: 0,
    totalInvitations: 0,
    activeJobs: 0,
    pendingInvitations: 0,
    successfulPlacements: 0
  };
  
  isLoading = true;
  invitationColumns = ['employee_name', 'job_title', 'manager', 'status', 'sent_date', 'actions'];

  constructor(
    private apiService: ApiService,
    private authService: AuthService,
    private snackBar: MatSnackBar,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.loadDashboardData();
  }

  private async loadDashboardData(): Promise<void> {
    try {
      this.isLoading = true;
      
      // Load all data sequentially to ensure they complete
      await this.loadAllInvitations();
      await this.loadAllJobs();
      await this.loadAllUsers();
      
      // Calculate statistics after all data is loaded
      this.calculateCompanyStats();
      
    } catch (error) {
      console.error('Error loading dashboard data:', error);
      this.showError('Failed to load dashboard data');
    } finally {
      this.isLoading = false;
    }
  }

  private async loadAllInvitations(): Promise<void> {
    return new Promise((resolve) => {
      this.apiService.getSentInvitations().subscribe({
        next: (invitations) => {
          this.allInvitations = invitations;
          resolve();
        },
        error: (error) => {
          console.error('Error loading invitations:', error);
          this.allInvitations = [];
          resolve();
        }
      });
    });
  }

  private async loadAllJobs(): Promise<void> {
    return new Promise((resolve) => {
      this.apiService.getJobs().subscribe({
        next: (jobs) => {
          this.allJobs = jobs;
          resolve();
        },
        error: (error) => {
          console.error('Error loading jobs:', error);
          this.allJobs = [];
          resolve();
        }
      });
    });
  }

  private async loadAllUsers(): Promise<void> {
    return new Promise((resolve) => {
      this.apiService.getAllUsers().subscribe({
        next: (users) => {
          this.allUsers = users;
          resolve();
        },
        error: (error) => {
          console.error('Error loading users:', error);
          this.allUsers = [];
          resolve();
        }
      });
    });
  }

  private calculateCompanyStats(): void {
    this.companyStats = {
      totalEmployees: this.allUsers.length,
      totalJobs: this.allJobs.length,
      totalInvitations: this.allInvitations.length,
      activeJobs: this.allJobs.filter(job => job.status === 'active').length,
      pendingInvitations: this.allInvitations.filter(inv => inv.status === 'pending').length,
      successfulPlacements: this.allInvitations.filter(inv => inv.status === 'accepted').length
    };
  }

  async viewInvitationDetails(invitationId: string): Promise<void> {
    // Navigate to invitation details page
    this.router.navigate(['/invitations', invitationId]);
  }

  async reassignJob(jobId: string, newManagerId: string): Promise<void> {
    try {
      this.apiService.reassignJob(jobId, newManagerId).subscribe({
        next: () => {
          this.showSuccess('Job reassigned successfully');
          this.loadDashboardData(); // Refresh data
        },
        error: (error) => {
          console.error('Error reassigning job:', error);
          this.showError('Failed to reassign job');
        }
      });
    } catch (error) {
      console.error('Error reassigning job:', error);
      this.showError('Failed to reassign job');
    }
  }

  getStatusClass(status: string): string {
    return status.toLowerCase().replace('_', '-');
  }

  getPendingInvitations(): Invitation[] {
    return this.allInvitations.filter(inv => inv.status === 'pending');
  }

  getRecentInvitations(): Invitation[] {
    return this.allInvitations
      .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
      .slice(0, 10);
  }

  async withdrawInvitation(invitationId: string): Promise<void> {
    try {
      // Call API to withdraw invitation
      // For now, just show a message and remove from local array
      this.allInvitations = this.allInvitations.filter(inv => inv.id !== invitationId);
      this.calculateCompanyStats();
      this.showSuccess('Invitation withdrawn successfully');
    } catch (error) {
      console.error('Error withdrawing invitation:', error);
      this.showError('Failed to withdraw invitation');
    }
  }

  async discoverCandidates(jobId: string): Promise<void> {
    try {
      this.showSuccess('Discovering candidates... You will be redirected to review matches.');
      
      // Trigger the matching algorithm
      this.apiService.triggerMatching(jobId).subscribe({
        next: (response) => {
          this.showSuccess('Matching completed! Reviewing candidates...');
          // Navigate to job matches page where HR can review and invite candidates
          this.router.navigate(['/jobs', jobId, 'matches']);
        },
        error: (error) => {
          console.error('Error triggering matching:', error);
          this.showError('Failed to discover candidates. Please try again.');
        }
      });
    } catch (error) {
      console.error('Error discovering candidates:', error);
      this.showError('Failed to discover candidates');
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
      duration: 3000,
      panelClass: ['error-snackbar']
    });
  }
}
