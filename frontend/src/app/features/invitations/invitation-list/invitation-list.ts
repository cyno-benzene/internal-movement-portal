import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatDialogModule, MatDialog } from '@angular/material/dialog';
import { MatBadgeModule } from '@angular/material/badge';
import { InvitationService } from '../../../core/services/invitation';
import { AuthService } from '../../../core/services/auth';
import { Invitation } from '../../../core/models/job.model';
import { User } from '../../../core/models/user.model';
// import { InvitationRespondComponent } from '../invitation-respond/invitation-respond';

@Component({
  selector: 'app-invitation-list',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatChipsModule,
    MatDialogModule,
    MatBadgeModule
  ],
  templateUrl: './invitation-list.html',
  styleUrl: './invitation-list.scss'
})
export class InvitationListComponent implements OnInit {
  invitations: Invitation[] = [];
  pendingInvitations: Invitation[] = [];
  loading = true;
  currentUser: User | null = null;

  constructor(
    private invitationService: InvitationService,
    private authService: AuthService,
    private dialog: MatDialog
  ) {}

  ngOnInit(): void {
    this.authService.currentUser$.subscribe(user => {
      this.currentUser = user;
    });
    
    this.loadInvitations();
    
    // Subscribe to invitation updates from service
    this.invitationService.invitations$.subscribe(invitations => {
      this.invitations = invitations;
      this.pendingInvitations = invitations.filter(inv => inv.status === 'pending');
      this.loading = false;
    });
  }

  loadInvitations(): void {
    this.loading = true;
    
    if (this.isEmployee()) {
      // Load invitations received by the employee
      this.invitationService.loadInvitations();
    } else {
      // Load invitations sent by HR/Admin
      this.invitationService.loadSentInvitations();
    }
  }

  openInvitation(invitation: Invitation): void {
    // TODO: Implement invitation dialog
    // const dialogRef = this.dialog.open(InvitationRespondComponent, {
    //   width: '600px',
    //   data: { invitation }
    // });

    // dialogRef.afterClosed().subscribe(result => {
    //   if (result) {
    //     this.loadInvitations(); // Refresh the list
    //   }
    // });
    console.log('Opening invitation:', invitation.id);
  }

  getStatusIcon(status: string): string {
    switch (status) {
      case 'pending': return 'schedule';
      case 'accepted': return 'check_circle';
      case 'declined': return 'cancel';
      default: return 'help';
    }
  }

  getStatusColor(status: string): string {
    switch (status) {
      case 'pending': return 'orange';
      case 'accepted': return 'green';
      case 'declined': return 'red';
      default: return 'gray';
    }
  }

  formatDate(dateString: string): string {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  }

  isEmployee(): boolean {
    return this.currentUser?.role === 'employee';
  }

  isManagerOrHR(): boolean {
    return this.currentUser?.role === 'manager' || this.currentUser?.role === 'hr' || this.currentUser?.role === 'admin';
  }

  getPageTitle(): string {
    return this.isEmployee() ? 'My Invitations' : 'Sent Invitations';
  }
}
