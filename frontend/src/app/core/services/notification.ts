import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { ApiService } from './api';

export interface Notification {
  id: string;
  content: string;
  read: boolean;
  created_at: string;
}

export interface ToastMessage {
  message: string;
  type: 'success' | 'error' | 'info' | 'warning';
  duration?: number;
}

@Injectable({
  providedIn: 'root'
})
export class NotificationService {
  private notificationsSubject = new BehaviorSubject<Notification[]>([]);
  public notifications$ = this.notificationsSubject.asObservable();

  private toastSubject = new BehaviorSubject<ToastMessage | null>(null);
  public toast$ = this.toastSubject.asObservable();

  constructor(private apiService: ApiService) {}

  loadNotifications(): void {
    this.apiService.getNotifications().subscribe({
      next: (notifications) => {
        this.notificationsSubject.next(notifications);
      },
      error: (error) => {
        console.error('Failed to load notifications:', error);
      }
    });
  }

  markAsRead(notificationIds: string[]): Observable<void> {
    return this.apiService.markNotificationsRead(notificationIds);
  }

  getUnreadCount(): number {
    const notifications = this.notificationsSubject.value;
    return notifications.filter(n => !n.read).length;
  }

  // Toast notifications
  showSuccess(message: string, duration = 3000): void {
    this.showToast({ message, type: 'success', duration });
  }

  showError(message: string, duration = 5000): void {
    this.showToast({ message, type: 'error', duration });
  }

  showInfo(message: string, duration = 3000): void {
    this.showToast({ message, type: 'info', duration });
  }

  showWarning(message: string, duration = 4000): void {
    this.showToast({ message, type: 'warning', duration });
  }

  private showToast(toast: ToastMessage): void {
    this.toastSubject.next(toast);
    
    if (toast.duration && toast.duration > 0) {
      setTimeout(() => {
        this.toastSubject.next(null);
      }, toast.duration);
    }
  }

  clearToast(): void {
    this.toastSubject.next(null);
  }
}
