import { Routes } from '@angular/router';
import { AuthGuard } from './core/guards/auth-guard';
import { RoleGuard } from './core/guards/role-guard';
import { AdminGuard } from './core/guards/admin-guard';
import { LoginComponent } from './features/auth/login/login';
import { UserManagementComponent } from './features/admin/user-management/user-management';
import { JobListComponent } from './features/jobs/job-list/job-list';
import { JobCreateComponent } from './features/jobs/job-create/job-create';
import { JobDetailsComponent } from './features/jobs/job-details/job-details';
import { JobMatchesComponent } from './features/jobs/job-matches/job-matches';
import { InvitationListComponent } from './features/invitations/invitation-list/invitation-list';
import { InvitationDetailComponent } from './features/invitations/invitation-detail/invitation-detail';
import { EmployeeDashboardComponent } from './features/employee/dashboard/employee-dashboard';
import { ManagerDashboardComponent } from './features/manager/dashboard/manager-dashboard';
import { HrDashboardComponent } from './features/hr/dashboard/hr-dashboard';
import { ProfileManagementComponent } from './features/profile/profile-management';
import { NotificationListComponent } from './features/notifications/notification-list';

export const routes: Routes = [
  { path: '', redirectTo: '/dashboard', pathMatch: 'full' },
  { path: 'login', component: LoginComponent },
  
  // Dashboard routes - role-based routing
  {
    path: 'dashboard',
    canActivate: [AuthGuard],
    children: [
      { 
        path: '', 
        redirectTo: 'employee', 
        pathMatch: 'full' 
      },
      { 
        path: 'employee', 
        component: EmployeeDashboardComponent 
      },
      {
        path: 'manager',
        component: ManagerDashboardComponent,
        canActivate: [RoleGuard],
        data: { roles: ['manager', 'admin'] }
      },
      {
        path: 'hr',
        component: HrDashboardComponent,
        canActivate: [RoleGuard],
        data: { roles: ['hr', 'admin'] }
      }
    ]
  },
  
  // Admin routes
  {
    path: 'admin',
    canActivate: [AuthGuard, AdminGuard],
    children: [
      { path: '', redirectTo: 'users', pathMatch: 'full' },
      { path: 'users', component: UserManagementComponent }
    ]
  },
  
  // Jobs routes - Role-based access
  {
    path: 'jobs',
    canActivate: [AuthGuard],
    children: [
      { 
        path: '', 
        component: JobListComponent,
        canActivate: [RoleGuard],
        data: { roles: ['manager', 'hr', 'admin'] }
      },
      { 
        path: 'create', 
        component: JobCreateComponent,
        canActivate: [RoleGuard],
        data: { roles: ['manager', 'admin'] } // HR excluded from job creation
      },
      { 
        path: ':id', 
        component: JobDetailsComponent,
        canActivate: [RoleGuard],
        data: { roles: ['manager', 'hr', 'admin'] }
      },
      { 
        path: 'edit/:id', 
        component: JobCreateComponent,
        canActivate: [RoleGuard],
        data: { roles: ['manager', 'admin'] } // HR excluded from job editing
      },
      { 
        path: ':id/matches', 
        component: JobMatchesComponent,
        canActivate: [RoleGuard],
        data: { roles: ['manager', 'hr', 'admin'] }
      },
      { path: ':id/discover', component: JobListComponent }, // Legacy - redirect to matches
      { path: ':id/shortlist', component: JobListComponent }, // Legacy - redirect to matches
    ]
  },

  // Invitations routes - Role-based access
  {
    path: 'invitations',
    canActivate: [AuthGuard],
    children: [
      { path: '', component: InvitationListComponent }, // My invitations (employee) / Sent invitations (manager/hr)
      { path: ':id', component: InvitationDetailComponent }, // View invitation details
      { path: ':id/respond', component: InvitationListComponent } // Respond to invitation (employee only)
    ]
  },
  
  // Profile routes
  {
    path: 'profile',
    canActivate: [AuthGuard],
    component: ProfileManagementComponent
  },
  
  // Notifications routes
  {
    path: 'notifications',
    canActivate: [AuthGuard],
    component: NotificationListComponent
  },
  
  // Legacy dashboard routes (redirect to new structure)
  {
    path: 'employee',
    redirectTo: '/dashboard/employee',
    pathMatch: 'full'
  },
  
  {
    path: 'manager',
    redirectTo: '/dashboard/manager',
    pathMatch: 'full'
  },
  
  {
    path: 'hr',
    redirectTo: '/dashboard/hr',
    pathMatch: 'full'
  },
  
  // Legacy routes redirect to appropriate new routes
  {
    path: 'applications',
    redirectTo: '/invitations',
    pathMatch: 'full'
  },
  
  {
    path: 'matched-jobs',
    redirectTo: '/invitations',
    pathMatch: 'full'
  },
  
  // Fallback routes
  { 
    path: 'unauthorized', 
    component: LoginComponent // Temporary redirect to login
  },
  { path: '**', redirectTo: '/dashboard' }
];
