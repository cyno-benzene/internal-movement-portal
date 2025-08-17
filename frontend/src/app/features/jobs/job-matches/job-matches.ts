import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTableModule } from '@angular/material/table';
import { MatChipsModule } from '@angular/material/chips';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatDialogModule, MatDialog } from '@angular/material/dialog';
import { SelectionModel } from '@angular/cdk/collections';
import { ApiService } from '../../../core/services/api';
import { AuthService } from '../../../core/services/auth';
import { Job } from '../../../core/models/job.model';
import { EmployeeCandidate } from '../../../core/models/job.model';

export interface JobMatch {
  employee_id: string;
  employee_name: string;
  employee_email: string;
  score: number;
  skills_match: string[];
  explanation?: {
    skill_matches: { skill: string; score: number }[];
    experience_score: number;
    total_score: number;
    reasons: string[];
  };
}

@Component({
  selector: 'app-job-matches',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatTableModule,
    MatChipsModule,
    MatProgressSpinnerModule,
    MatSnackBarModule,
    MatCheckboxModule,
    MatDialogModule
  ],
  templateUrl: './job-matches.html',
  styleUrls: ['./job-matches.scss']
})
export class JobMatchesComponent implements OnInit {
  job: Job | null = null;
  matches: JobMatch[] = [];
  isLoading = true;
  isRunningMatch = false;
  jobId: string;
  selection = new SelectionModel<JobMatch>(true, []);
  displayedColumns: string[] = ['select', 'employee_name', 'score', 'skills_match', 'explanation', 'actions'];
  currentUser: any = null;
  isHR = false;
  isManager = false;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private apiService: ApiService,
    private authService: AuthService,
    private snackBar: MatSnackBar,
    private dialog: MatDialog
  ) {
    this.jobId = this.route.snapshot.paramMap.get('id') || '';
    this.currentUser = this.authService.getCurrentUser();
    this.isHR = this.currentUser?.role === 'hr' || this.currentUser?.role === 'admin';
    this.isManager = this.currentUser?.role === 'manager';
  }

  ngOnInit(): void {
    this.loadJobDetails();
    this.loadExistingMatches();
  }

  private async loadJobDetails(): Promise<void> {
    try {
      this.apiService.getJob(this.jobId).subscribe({
        next: (job) => {
          this.job = job;
        },
        error: (error) => {
          console.error('Error loading job:', error);
          this.showError('Failed to load job details');
        }
      });
    } catch (error) {
      console.error('Error loading job details:', error);
      this.showError('Failed to load job details');
    }
  }

  private async loadExistingMatches(): Promise<void> {
    try {
      this.isLoading = true;
      this.apiService.getJobMatches(this.jobId).subscribe({
        next: (matches) => {
          this.matches = matches;
          this.isLoading = false;
        },
        error: (error) => {
          console.error('Error loading matches:', error);
          this.matches = [];
          this.isLoading = false;
        }
      });
    } catch (error) {
      console.error('Error loading matches:', error);
      this.isLoading = false;
    }
  }

  async triggerNewMatching(): Promise<void> {
    if (!this.job) return;
    
    const confirmed = confirm(
      `Run AI Matching for "${this.job.title}"?\n\n` +
      `This will analyze all employee profiles and find the best candidates ` +
      `based on skills, experience, and career aspirations.\n\n` +
      `This may take a few moments...`
    );

    if (!confirmed) return;

    try {
      this.isRunningMatch = true;
      this.apiService.triggerMatching(this.jobId).subscribe({
        next: () => {
          this.showSuccess('Matching completed! Loading results...');
          // Reload matches after a short delay
          setTimeout(() => {
            this.loadExistingMatches();
            this.isRunningMatch = false;
          }, 2000);
        },
        error: (error) => {
          console.error('Error triggering matching:', error);
          this.showError('Failed to run matching algorithm');
          this.isRunningMatch = false;
        }
      });
    } catch (error) {
      console.error('Error triggering matching:', error);
      this.showError('Failed to run matching algorithm');
      this.isRunningMatch = false;
    }
  }

  getScoreColor(score: number): string {
    if (score >= 80) return 'high-score';
    if (score >= 60) return 'medium-score';
    return 'low-score';
  }

  getScoreIcon(score: number): string {
    if (score >= 80) return 'star';
    if (score >= 60) return 'star_half';
    return 'star_border';
  }

  isAllSelected(): boolean {
    const numSelected = this.selection.selected.length;
    const numRows = this.matches.length;
    return numSelected === numRows;
  }

  masterToggle(): void {
    this.isAllSelected() ?
      this.selection.clear() :
      this.matches.forEach(row => this.selection.select(row));
  }

  sendInvitations(): void {
    const selectedCandidates = this.selection.selected;
    if (selectedCandidates.length === 0) {
      this.showError('Please select at least one candidate to invite');
      return;
    }

    const employeeIds = selectedCandidates.map(c => c.employee_id);
    
    // TODO: Implement invitation dialog/flow
    this.showSuccess(`Invitations will be sent to ${selectedCandidates.length} candidates`);
    
    // For now, just clear selection
    this.selection.clear();
  }

  viewEmployeeProfile(employeeId: string): void {
    // TODO: Navigate to employee profile or open dialog
    this.showSuccess('Opening employee profile...');
  }

  inviteSelected(): void {
    const selectedCandidates = this.selection.selected;
    if (selectedCandidates.length === 0) {
      this.showError('Please select at least one candidate to invite');
      return;
    }

    const employeeIds = selectedCandidates.map(c => c.employee_id);
    
    // TODO: Implement invitation dialog/flow
    this.showSuccess(`Invitations will be sent to ${selectedCandidates.length} candidates`);
    
    // For now, just clear selection
    this.selection.clear();
  }

  inviteSingle(match: JobMatch): void {
    // TODO: Implement single invitation flow
    this.showSuccess(`Invitation will be sent to ${match.employee_name}`);
  }

  viewProfile(employeeId: string): void {
    // TODO: Navigate to employee profile or open dialog
    this.showSuccess('Opening employee profile...');
  }

  refreshMatches(): void {
    this.loadExistingMatches();
  }

  getScoreClass(score: number): string {
    if (score >= 0.8) return 'score-high';
    if (score >= 0.6) return 'score-medium';
    return 'score-low';
  }

  goBack(): void {
    this.router.navigate(['/dashboard/hr']);
  }

  private showSuccess(message: string): void {
    this.snackBar.open(message, 'Close', {
      duration: 3000,
      panelClass: ['success-snackbar']
    });
  }

  private showError(message: string): void {
    this.snackBar.open(message, 'Close', {
      duration: 5000,
      panelClass: ['error-snackbar']
    });
  }
}
