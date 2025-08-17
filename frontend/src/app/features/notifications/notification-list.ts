import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatListModule } from '@angular/material/list';
import { MatBadgeModule } from '@angular/material/badge';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { NotificationService, Notification } from '../../core/services/notification';

@Component({
  selector: 'app-notification-list',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatListModule,
    MatBadgeModule,
    MatSnackBarModule
  ],
  templateUrl: './notification-list.html',
  styleUrls: ['./notification-list.scss']
})
export class NotificationListComponent implements OnInit {
  notifications: Notification[] = [];
  isLoading = true;

  constructor(
    private notificationService: NotificationService,
    private snackBar: MatSnackBar,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.loadNotifications();
    this.subscribeToNotifications();
  }

  private loadNotifications(): void {
    this.notificationService.loadNotifications();
  }

  private subscribeToNotifications(): void {
    this.notificationService.notifications$.subscribe({
      next: (notifications) => {
        this.notifications = notifications.sort((a, b) => 
          new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        );
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error loading notifications:', error);
        this.showError('Failed to load notifications');
        this.isLoading = false;
      }
    });
  }

  async markAsRead(notification: Notification): Promise<void> {
    if (!notification.read) {
      try {
        this.notificationService.markAsRead([notification.id]).subscribe({
          next: () => {
            notification.read = true;
            this.showSuccess('Notification marked as read');
          },
          error: (error) => {
            console.error('Error marking notification as read:', error);
            this.showError('Failed to mark notification as read');
          }
        });
      } catch (error) {
        console.error('Error marking notification as read:', error);
        this.showError('Failed to mark notification as read');
      }
    }
  }

  onNotificationClick(notification: Notification): void {
    // Mark as read first
    this.markAsRead(notification);
    
    // Navigate based on notification content
    this.navigateToNotificationTarget(notification);
  }

  navigateToNotificationTarget(notification: Notification): void {
    const content = notification.content.toLowerCase();
    
    // Parse notification content to determine navigation target
    if (content.includes('application') && content.includes('requires hr review')) {
      // Application review notification - navigate to applications page
      this.router.navigate(['/applications']);
    } else if (content.includes('invitation')) {
      // Invitation related notification - navigate to invitations
      this.router.navigate(['/invitations']);
    } else if (content.includes('job') && content.includes('match')) {
      // Job matching notification - navigate to jobs
      this.router.navigate(['/jobs']);
    } else if (content.includes('profile')) {
      // Profile related notification - navigate to profile
      this.router.navigate(['/profile']);
    } else {
      // Default fallback - stay on notifications page
      this.showInfo('Notification details viewed');
    }
  }

  async markAllAsRead(): Promise<void> {
    const unreadIds = this.notifications
      .filter(n => !n.read)
      .map(n => n.id);

    if (unreadIds.length === 0) {
      this.showInfo('No unread notifications');
      return;
    }

    try {
      this.notificationService.markAsRead(unreadIds).subscribe({
        next: () => {
          this.notifications.forEach(n => n.read = true);
          this.showSuccess('All notifications marked as read');
        },
        error: (error) => {
          console.error('Error marking all notifications as read:', error);
          this.showError('Failed to mark all notifications as read');
        }
      });
    } catch (error) {
      console.error('Error marking all notifications as read:', error);
      this.showError('Failed to mark all notifications as read');
    }
  }

  getUnreadNotifications(): Notification[] {
    return this.notifications.filter(n => !n.read);
  }

  getReadNotifications(): Notification[] {
    return this.notifications.filter(n => n.read);
  }

  getNotificationIcon(notification: Notification): string {
    if (notification.content.toLowerCase().includes('application')) {
      return 'assignment';
    } else if (notification.content.toLowerCase().includes('job')) {
      return 'work';
    } else if (notification.content.toLowerCase().includes('profile')) {
      return 'person';
    } else {
      return 'notifications';
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

  private showInfo(message: string): void {
    this.snackBar.open(message, 'Close', {
      duration: 3000,
      panelClass: ['info-snackbar']
    });
  }
}
