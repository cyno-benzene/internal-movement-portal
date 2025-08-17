import { Component, Inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatDialogModule, MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { InvitationService } from '../../../core/services/invitation';
import { Invitation } from '../../../core/models/job.model';

@Component({
  selector: 'app-invitation-respond',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatDialogModule,
    MatButtonModule,
    MatFormFieldModule,
    MatInputModule,
    MatIconModule,
    MatCardModule,
    MatChipsModule
  ],
  templateUrl: './invitation-respond.html',
  styleUrl: './invitation-respond.scss'
})
export class InvitationRespondComponent {
  invitation: Invitation;
  reason = '';
  submitting = false;

  constructor(
    public dialogRef: MatDialogRef<InvitationRespondComponent>,
    @Inject(MAT_DIALOG_DATA) public data: { invitation: Invitation },
    private invitationService: InvitationService
  ) {
    this.invitation = data.invitation;
  }

  accept(): void {
    this.respond('accepted');
  }

  decline(): void {
    if (!this.reason.trim()) {
      return; // Require reason for declining
    }
    this.respond('declined');
  }

  private respond(response: 'accepted' | 'declined'): void {
    this.submitting = true;
    
    this.invitationService.respondToInvitation(
      this.invitation.id, 
      response, 
      this.reason.trim() || undefined
    ).subscribe({
      next: () => {
        this.dialogRef.close(true);
      },
      error: (error) => {
        console.error('Error responding to invitation:', error);
        this.submitting = false;
      }
    });
  }

  close(): void {
    this.dialogRef.close(false);
  }

  formatDate(dateString: string): string {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  }
}
