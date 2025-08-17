import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { ApiService } from '../../../core/services/api';
import { Job } from '../../../core/models/job.model';

@Component({
  selector: 'app-job-create',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatChipsModule,
    MatIconModule,
    MatSnackBarModule
  ],
  templateUrl: './job-create.html',
  styleUrl: './job-create.scss'
})
export class JobCreateComponent implements OnInit {
  jobForm: FormGroup;
  skills: string[] = [];
  editingJobId: string | null = null;
  isEditing = false;

  constructor(
    private fb: FormBuilder,
    private apiService: ApiService,
    private router: Router,
    private route: ActivatedRoute,
    private snackBar: MatSnackBar
  ) {
    this.jobForm = this.fb.group({
      title: ['', Validators.required],
      team: ['', Validators.required],
      description: ['', Validators.required],
      skillInput: ['']
    });
  }

  ngOnInit(): void {
    // Check if we're editing an existing job
    this.editingJobId = this.route.snapshot.paramMap.get('id');
    if (this.editingJobId) {
      this.isEditing = true;
      this.loadJobForEditing(this.editingJobId);
    }
  }

  loadJobForEditing(jobId: string): void {
    this.apiService.getJob(jobId).subscribe({
      next: (job: Job) => {
        this.jobForm.patchValue({
          title: job.title,
          team: job.team,
          description: job.description
        });
        this.skills = job.required_skills || [];
      },
      error: (error) => {
        console.error('Error loading job for editing:', error);
        this.snackBar.open('Failed to load job details', 'Close', { duration: 3000 });
        this.router.navigate(['/jobs']);
      }
    });
  }

  addSkill(): void {
    const skillInput = this.jobForm.get('skillInput');
    if (skillInput?.value && skillInput.value.trim()) {
      const skill = skillInput.value.trim();
      if (!this.skills.includes(skill)) {
        this.skills.push(skill);
      }
      skillInput.setValue('');
    }
  }

  removeSkill(skill: string): void {
    const index = this.skills.indexOf(skill);
    if (index >= 0) {
      this.skills.splice(index, 1);
    }
  }

  onSubmit(): void {
    if (this.jobForm.valid) {
      const jobData = {
        title: this.jobForm.value.title,
        team: this.jobForm.value.team,
        description: this.jobForm.value.description,
        required_skills: this.skills
      };

      if (this.isEditing && this.editingJobId) {
        // Update existing job
        this.apiService.updateJob(this.editingJobId, jobData).subscribe({
          next: (job) => {
            this.snackBar.open('Job updated successfully', 'Close', { duration: 3000 });
            this.router.navigate(['/jobs']);
          },
          error: (error) => {
            console.error('Error updating job:', error);
            this.snackBar.open('Failed to update job', 'Close', { duration: 3000 });
          }
        });
      } else {
        // Create new job
        this.apiService.createJob(jobData).subscribe({
          next: (job) => {
            this.snackBar.open('Job created successfully', 'Close', { duration: 3000 });
            this.router.navigate(['/jobs']);
          },
          error: (error) => {
            console.error('Error creating job:', error);
            this.snackBar.open('Failed to create job', 'Close', { duration: 3000 });
          }
        });
      }
    }
  }

  onCancel(): void {
    this.router.navigate(['/jobs']);
  }
}
