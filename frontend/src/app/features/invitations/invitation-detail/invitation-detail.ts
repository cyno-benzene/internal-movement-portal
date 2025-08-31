import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { InvitationService } from '../../../core/services/invitation';
import { Invitation } from '../../../core/models/job.model';

@Component({
  selector: 'app-invitation-detail',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatChipsModule,
    MatProgressSpinnerModule,
    MatSnackBarModule
  ],
  templateUrl: './invitation-detail.html',
  styleUrls: ['./invitation-detail.scss']
})
export class InvitationDetailComponent implements OnInit {
  invitation: Invitation | null = null;
  isLoading = true;
  invitationId: string;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private invitationService: InvitationService,
    private snackBar: MatSnackBar
  ) {
    this.invitationId = this.route.snapshot.paramMap.get('id') || '';
  }

  ngOnInit(): void {
    this.loadInvitationDetails();
  }

  private async loadInvitationDetails(): Promise<void> {
    try {
      this.isLoading = true;
      
      // For now, we'll simulate loading the invitation
      // In a real app, this would call the invitation service
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Mock invitation data - replace with actual API call
      this.invitation = {
        id: this.invitationId,
        employee: {
          id: '1',
          name: 'John Doe',
          email: 'john.doe@company.com',
          role: 'employee',
          full_name: 'John Doe'
        },
        job: {
          id: '1',
          title: 'Senior Frontend Developer',
          team: 'Frontend Team',
          manager_name: 'Jane Smith',
          department: 'Engineering',
          description: 'We are looking for an experienced frontend developer to join our team and help build the next generation of our web applications.',
          employment_type: 'Full-time',
          salary_range: '$80,000 - $120,000',
          created_at: new Date().toISOString(),
          required_skills: ['React', 'TypeScript', 'Node.js', 'Leadership']
        },
        inviter: {
          id: '2',
          name: 'Jane Smith',
          email: 'jane.smith@company.com',
          role: 'manager',
          full_name: 'Jane Smith',
          current_job_title: 'Engineering Manager'
        },
        status: 'pending',
        created_at: new Date().toISOString(),
        personal_message: 'Based on your excellent work on the current project, we would like to invite you to consider this exciting opportunity in our frontend team.'
      };
      
    } catch (error) {
      console.error('Error loading invitation details:', error);
      this.showError('Failed to load invitation details');
    } finally {
      this.isLoading = false;
    }
  }

  getStatusColor(status: string): string {
    switch (status) {
      case 'pending': return 'primary';
      case 'accepted': return 'accent';
      case 'declined': return 'warn';
      default: return 'primary';
    }
  }

  goBack(): void {
    this.router.navigate(['/invitations']);
  }

  private showError(message: string): void {
    this.snackBar.open(message, 'Close', {
      duration: 5000,
      panelClass: ['error-snackbar']
    });
  }
}
