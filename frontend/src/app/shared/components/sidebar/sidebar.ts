import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MatListModule } from '@angular/material/list';
import { MatIconModule } from '@angular/material/icon';
import { AuthService } from '../../../core/services/auth';
import { User } from '../../../core/models/user.model';

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    MatListModule,
    MatIconModule
  ],
  templateUrl: './sidebar.html',
  styleUrl: './sidebar.scss'
})
export class SidebarComponent implements OnInit {
  currentUser: User | null = null;

  constructor(private authService: AuthService) {}

  ngOnInit(): void {
    this.authService.currentUser$.subscribe(user => {
      this.currentUser = user;
    });
  }

  hasRole(roles: string[]): boolean {
    return this.authService.hasRole(roles);
  }

  getDashboardRoute(): string {
    if (!this.currentUser) return '/login';
    
    switch (this.currentUser.role) {
      case 'admin':
        return '/admin';
      case 'hr':
        return '/hr';
      case 'manager':
        return '/manager';
      default:
        return '/employee';
    }
  }
}
