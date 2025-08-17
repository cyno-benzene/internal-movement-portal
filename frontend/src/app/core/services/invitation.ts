import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { ApiService } from './api';
import { AuthService } from './auth';
import { Invitation } from '../models/job.model';
import { NotificationService } from './notification';

@Injectable({
  providedIn: 'root'
})
export class InvitationService {
  private invitationsSubject = new BehaviorSubject<Invitation[]>([]);
  public invitations$ = this.invitationsSubject.asObservable();

  constructor(
    private apiService: ApiService,
    private authService: AuthService,
    private notificationService: NotificationService
  ) {}

  loadInvitations(): void {
    const currentUser = this.authService.getCurrentUser();
    if (!currentUser) return;

    // For employees, load invitations they've received
    // For managers/HR, load invitations they've sent
    const apiCall = currentUser.role === 'employee' 
      ? this.apiService.getMyInvitations() 
      : this.apiService.getSentInvitations();

    apiCall.subscribe({
      next: (invitations) => {
        this.invitationsSubject.next(invitations);
      },
      error: (error) => {
        console.error('Error loading invitations:', error);
        this.notificationService.showError('Failed to load invitations');
      }
    });
  }

  loadSentInvitations(): void {
    // Load invitations sent by HR/Admin
    this.apiService.getSentInvitations().subscribe({
      next: (invitations) => {
        this.invitationsSubject.next(invitations);
      },
      error: (error) => {
        console.error('Error loading sent invitations:', error);
        this.notificationService.showError('Failed to load sent invitations');
      }
    });
  }

  respondToInvitation(invitationId: string, response: 'accepted' | 'declined', reason?: string): Observable<void> {
    return new Observable(observer => {
      this.apiService.respondToInvitation(invitationId, response, reason).subscribe({
        next: () => {
          // Refresh invitations after response
          this.loadInvitations();
          
          const message = response === 'accepted' 
            ? 'Invitation accepted successfully!' 
            : 'Invitation declined.';
          this.notificationService.showSuccess(message);
          
          observer.next();
          observer.complete();
        },
        error: (error) => {
          console.error('Error responding to invitation:', error);
          this.notificationService.showError('Failed to respond to invitation');
          observer.error(error);
        }
      });
    });
  }

  getPendingInvitations(): Invitation[] {
    return this.invitationsSubject.value.filter(inv => inv.status === 'pending');
  }

  getInvitationById(id: string): Invitation | undefined {
    return this.invitationsSubject.value.find(inv => inv.id === id);
  }

  getInvitationCounts(): { pending: number; total: number } {
    const invitations = this.invitationsSubject.value;
    return {
      pending: invitations.filter(inv => inv.status === 'pending').length,
      total: invitations.length
    };
  }
}
