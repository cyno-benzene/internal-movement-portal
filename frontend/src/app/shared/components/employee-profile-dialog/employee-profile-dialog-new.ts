import { Component, Inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MAT_DIALOG_DATA, MatDialogRef, MatDialogModule } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { ApiService } from '../../../core/services/api';
import { EmployeeProfile } from '../../../core/models/user.model';

export interface EmployeeProfileDialogData {
  employeeId: string;
  employeeName: string;
  employeeEmail: string;
  matchScore?: number;
  skillsMatch?: string[];
  explanation?: {
    skill_matches: { skill: string; score: number }[];
    experience_score: number;
    total_score: number;
    reasons: string[];
  };
}

@Component({
  selector: 'app-employee-profile-dialog',
  standalone: true,
  imports: [
    CommonModule,
    MatDialogModule,
    MatButtonModule,
    MatIconModule,
    MatCardModule,
    MatChipsModule,
    MatProgressSpinnerModule
  ],
  templateUrl: './employee-profile-dialog.html',
  styleUrls: ['./employee-profile-dialog.scss']
})
export class EmployeeProfileDialogComponent {
  profile: EmployeeProfile | null = null;
  loading = true;
  error: string | null = null;

  constructor(
    private dialogRef: MatDialogRef<EmployeeProfileDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: EmployeeProfileDialogData,
    private apiService: ApiService
  ) {
    this.loadEmployeeProfile();
  }

  private loadEmployeeProfile(): void {
    this.loading = true;
    this.error = null;
    
    this.apiService.getProfile(this.data.employeeId).subscribe({
      next: (profile) => {
        this.profile = profile;
        this.loading = false;
      },
      error: (error) => {
        console.error('Error loading employee profile:', error);
        this.error = 'Failed to load employee profile. Please try again.';
        this.loading = false;
        
        // Fallback profile with basic data
        this.profile = {
          id: this.data.employeeId,
          email: this.data.employeeEmail,
          name: this.data.employeeName,
          role: '',
          technical_skills: this.data.skillsMatch || [],
          achievements: [],
          years_experience: 0,
          past_companies: [],
          certifications: [],
          education: [],
          publications: [],
          career_aspirations: '',
          location: '',
          current_job_title: '',
          preferred_roles: [],
          visibility_opt_out: false,
          parsed_resume: null,
          updated_at: new Date().toISOString()
        };
      }
    });
  }

  getOtherSkills(): string[] {
    if (!this.profile?.technical_skills) return [];
    if (!this.data.skillsMatch) return this.profile.technical_skills;
    
    return this.profile.technical_skills.filter(skill => 
      !this.data.skillsMatch!.includes(skill)
    );
  }

  getScoreClass(score: number): string {
    if (score >= 80) return 'score-high';
    if (score >= 60) return 'score-medium';
    return 'score-low';
  }

  close(): void {
    this.dialogRef.close();
  }
}
