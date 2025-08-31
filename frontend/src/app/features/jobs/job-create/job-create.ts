import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';
import { Location, CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { MatSelectModule } from '@angular/material/select';
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
    MatSelectModule,
    MatSnackBarModule
  ],
  templateUrl: './job-create.html',
  styleUrl: './job-create.scss'
})
export class JobCreateComponent implements OnInit {
  jobForm: FormGroup;
  requiredSkills: string[] = [];
  optionalSkills: string[] = [];
  preferredCertifications: string[] = [];
  editingJobId: string | null = null;
  isEditing = false;

  constructor(
    private fb: FormBuilder,
    private apiService: ApiService,
    private router: Router,
    private route: ActivatedRoute,
    private location: Location,
    private snackBar: MatSnackBar
  ) {
    this.jobForm = this.fb.group({
      title: ['', Validators.required],
      team: ['', Validators.required],
      description: ['', Validators.required],
      note: [''],
      min_years_experience: [0, [Validators.min(0)]],
      priority: ['normal'],
      skillInput: [''],
      optionalSkillInput: [''],
      certificationInput: ['']
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
          description: job.description,
          note: job.note,
          min_years_experience: job.min_years_experience,
          priority: job.priority || 'normal'
        });
        this.requiredSkills = job.required_skills || [];
        this.optionalSkills = job.optional_skills || [];
        this.preferredCertifications = job.preferred_certifications || [];
      },
      error: (error) => {
        console.error('Error loading job for editing:', error);
        this.snackBar.open('Failed to load job details', 'Close', { duration: 3000 });
        this.router.navigate(['/jobs']);
      }
    });
  }

  addSkill(skillType: 'required' | 'optional' | 'certification'): void {
    let inputControl: string;
    let skillArray: string[];

    switch (skillType) {
      case 'required':
        inputControl = 'skillInput';
        skillArray = this.requiredSkills;
        break;
      case 'optional':
        inputControl = 'optionalSkillInput';
        skillArray = this.optionalSkills;
        break;
      case 'certification':
        inputControl = 'certificationInput';
        skillArray = this.preferredCertifications;
        break;
    }

    const input = this.jobForm.get(inputControl);
    if (input?.value && input.value.trim()) {
      const skill = input.value.trim();
      if (!skillArray.includes(skill)) {
        skillArray.push(skill);
      }
      input.setValue('');
    }
  }

  removeSkill(skillType: 'required' | 'optional' | 'certification', skill: string): void {
    let skillArray: string[];

    switch (skillType) {
      case 'required':
        skillArray = this.requiredSkills;
        break;
      case 'optional':
        skillArray = this.optionalSkills;
        break;
      case 'certification':
        skillArray = this.preferredCertifications;
        break;
    }

    const index = skillArray.indexOf(skill);
    if (index >= 0) {
      skillArray.splice(index, 1);
    }
  }

  onSubmit(): void {
    if (this.jobForm.valid) {
      const jobData = {
        title: this.jobForm.value.title,
        team: this.jobForm.value.team,
        description: this.jobForm.value.description,
        note: this.jobForm.value.note,
        min_years_experience: this.jobForm.value.min_years_experience,
        priority: this.jobForm.value.priority,
        required_skills: this.requiredSkills,
        optional_skills: this.optionalSkills,
        preferred_certifications: this.preferredCertifications
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
    this.location.back();
  }
}
