import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { AuthService } from '../../../core/services/auth';
import { interval, Subscription } from 'rxjs';

@Component({
  selector: 'app-session-status',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule
  ],
  template: `
    <div class="session-status" *ngIf="isAuthenticated">
      <mat-card class="status-card">
        <mat-card-content>
          <div class="session-info">
            <mat-icon [class]="getStatusIcon()">{{ getStatusIcon() }}</mat-icon>
            <span class="time-display">{{ timeDisplay }}</span>
            <button mat-icon-button (click)="refreshSession()" 
                    [disabled]="!canRefresh"
                    matTooltip="Extend session">
              <mat-icon>refresh</mat-icon>
            </button>
          </div>
          <div class="session-bar">
            <div class="session-progress" [style.width.%]="progressPercentage"></div>
          </div>
        </mat-card-content>
      </mat-card>
    </div>
  `,
  styles: [`
    .session-status {
      position: fixed;
      top: 10px;
      right: 10px;
      z-index: 1000;
    }

    .status-card {
      min-width: 200px;
      padding: 8px;
    }

    .session-info {
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .time-display {
      flex: 1;
      font-size: 14px;
      font-weight: 500;
    }

    .session-bar {
      height: 4px;
      background-color: #e0e0e0;
      border-radius: 2px;
      margin-top: 8px;
      overflow: hidden;
    }

    .session-progress {
      height: 100%;
      transition: width 0.3s ease;
      border-radius: 2px;
    }

    .status-good {
      color: #4caf50;
    }

    .status-warning {
      color: #ff9800;
    }

    .status-critical {
      color: #f44336;
    }

    .session-progress {
      background-color: var(--progress-color, #4caf50);
    }
  `]
})
export class SessionStatusComponent implements OnInit, OnDestroy {
  timeDisplay = '';
  progressPercentage = 100;
  isAuthenticated = false;
  canRefresh = true;
  
  private updateSubscription?: Subscription;
  private readonly SESSION_DURATION_MS = 30 * 1000; // 30 seconds for testing

  constructor(private authService: AuthService) {}

  ngOnInit(): void {
    this.updateSubscription = interval(1000).subscribe(() => {
      this.updateSessionStatus();
    });
    this.updateSessionStatus();
  }

  ngOnDestroy(): void {
    if (this.updateSubscription) {
      this.updateSubscription.unsubscribe();
    }
  }

  private updateSessionStatus(): void {
    this.isAuthenticated = this.authService.isAuthenticated();
    
    if (!this.isAuthenticated) {
      return;
    }

    const timeRemaining = this.authService.getTimeUntilExpiration();
    this.progressPercentage = Math.max(0, (timeRemaining / this.SESSION_DURATION_MS) * 100);
    
    if (timeRemaining > 0) {
      const minutes = Math.floor(timeRemaining / (60 * 1000));
      const seconds = Math.floor((timeRemaining % (60 * 1000)) / 1000);
      this.timeDisplay = `${minutes}:${seconds.toString().padStart(2, '0')}`;
    } else {
      this.timeDisplay = 'Expired';
      this.progressPercentage = 0;
    }
  }

  getStatusIcon(): string {
    const timeRemaining = this.authService.getTimeUntilExpiration();
    const minutes = Math.floor(timeRemaining / (60 * 1000));
    
    if (minutes > 10) return 'schedule';
    if (minutes > 5) return 'schedule';
    if (minutes > 0) return 'warning';
    return 'error';
  }

  refreshSession(): void {
    this.canRefresh = false;
    // The refresh logic is handled in the AuthService
    setTimeout(() => {
      this.canRefresh = true;
    }, 5000);
  }
}
