import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatGridListModule } from '@angular/material/grid-list';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatBadgeModule } from '@angular/material/badge';
import { ApiService } from '../../../core/services/api';
import { AuthService } from '../../../core/services/auth';
import { InvitationService } from '../../../core/services/invitation';
import { Invitation } from '../../../core/models/job.model';
import { User, EmployeeProfile } from '../../../core/models/user.model';

@Component({
  selector: 'app-employee-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatGridListModule,
    MatSnackBarModule,
    MatBadgeModule
  ],
  templateUrl: './employee-dashboard.html',
  styleUrls: ['./employee-dashboard.scss']
})
export class EmployeeDashboardComponent implements OnInit {
  pendingInvitations: Invitation[] = [];
  recentInvitations: Invitation[] = [];
  profileCompleteness: number = 0;
  currentUser: User | null = null;
  userProfile: EmployeeProfile | null = null;
  isLoading = true;

  constructor(
    private apiService: ApiService,
    private authService: AuthService,
    private invitationService: InvitationService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    this.currentUser = this.authService.getCurrentUser();
    this.loadDashboardData();
  }

  private async loadDashboardData(): Promise<void> {
    try {
      this.isLoading = true;
      
      // Load user profile
      this.userProfile = (await this.apiService.getMyProfile().toPromise()) || null;
      
      // Load invitations
      this.invitationService.loadInvitations();
      
      // Subscribe to invitation updates
      this.invitationService.invitations$.subscribe(invitations => {
        this.pendingInvitations = invitations.filter(inv => inv.status === 'pending');
        this.recentInvitations = invitations
          .filter(inv => inv.status !== 'pending')
          .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
          .slice(0, 5);
      });

      // Calculate profile completeness
      this.calculateProfileCompleteness();
      
    } catch (error) {
      console.error('Error loading dashboard data:', error);
      this.snackBar.open('Error loading dashboard data', 'Close', { duration: 3000 });
    } finally {
      this.isLoading = false;
    }
  }

  private calculateProfileCompleteness(): void {
    if (!this.userProfile) {
      this.profileCompleteness = 0;
      return;
    }

    const fields = [
      this.userProfile.name,
      this.userProfile.email,
      this.userProfile.current_job_title,
      this.userProfile.location,
      this.userProfile.technical_skills,
      this.userProfile.preferred_roles,
      this.userProfile.career_aspirations
    ];

    const completedFields = fields.filter(field => {
      if (Array.isArray(field)) {
        return field && field.length > 0;
      }
      return field && field.trim() !== '';
    }).length;

    this.profileCompleteness = Math.round((completedFields / fields.length) * 100);
  }

  updateProfile(): void {
    // Navigate to profile page or open profile dialog
    // For now, just show a message
    this.snackBar.open('Navigate to profile page to update your information', 'Close', { duration: 3000 });
  }

  formatDate(dateString: string): string {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  }

  getInvitationStatusIcon(status: string): string {
    switch (status) {
      case 'pending': return 'schedule';
      case 'accepted': return 'check_circle';
      case 'declined': return 'cancel';
      default: return 'help';
    }
  }

  getInvitationStatusColor(status: string): string {
    switch (status) {
      case 'pending': return 'orange';
      case 'accepted': return 'green';
      case 'declined': return 'red';
      default: return 'gray';
    }
  }
}
