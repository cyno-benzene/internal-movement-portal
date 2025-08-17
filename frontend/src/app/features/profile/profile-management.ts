import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, FormArray, Validators } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { ApiService } from '../../core/services/api';
import { AuthService } from '../../core/services/auth';
import { EmployeeProfile } from '../../core/models/user.model';

@Component({
  selector: 'app-profile-management',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatButtonModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatChipsModule,
    MatIconModule,
    MatSnackBarModule
  ],
  templateUrl: './profile-management.html',
  styleUrls: ['./profile-management.scss']
})
export class ProfileManagementComponent implements OnInit {
  profileForm!: FormGroup;
  userProfile: EmployeeProfile | null = null;
  isLoading = true;
  isSaving = false;

  constructor(
    private formBuilder: FormBuilder,
    private apiService: ApiService,
    private authService: AuthService,
    private snackBar: MatSnackBar
  ) {
    this.initializeForm();
  }

  ngOnInit(): void {
    this.loadUserProfile();
  }

  private initializeForm(): void {
    this.profileForm = this.formBuilder.group({
      name: ['', [Validators.required]],
      email: ['', [Validators.required, Validators.email]],
      technical_skills: this.formBuilder.array([]),
      achievements: this.formBuilder.array([]),
      years_experience: [0, [Validators.min(0)]],
      past_companies: this.formBuilder.array([]),
      certifications: this.formBuilder.array([]),
      education: this.formBuilder.array([]),
      publications: this.formBuilder.array([]),
      career_aspirations: [''],
      location: ['']
    });
  }

  private async loadUserProfile(): Promise<void> {
    try {
      this.isLoading = true;
      this.apiService.getMyProfile().subscribe({
        next: (profile) => {
          this.userProfile = profile;
          this.populateForm(profile);
        },
        error: (error) => {
          console.error('Error loading profile:', error);
          this.showError('Failed to load profile');
        },
        complete: () => {
          this.isLoading = false;
        }
      });
    } catch (error) {
      console.error('Error loading profile:', error);
      this.showError('Failed to load profile');
      this.isLoading = false;
    }
  }

  private populateForm(profile: EmployeeProfile): void {
    this.profileForm.patchValue({
      name: profile.name,
      email: profile.email,
      years_experience: profile.years_experience,
      career_aspirations: profile.career_aspirations || '',
      location: profile.location || ''
    });

    // Populate arrays
    this.setArrayField('technical_skills', profile.technical_skills || []);
    this.setArrayField('achievements', profile.achievements || []);
    this.setArrayField('certifications', profile.certifications || []);
    this.setArrayField('publications', profile.publications || []);
    this.setArrayField('past_companies', profile.past_companies || []);
    this.setArrayField('education', profile.education || []);
  }

  private setArrayField(fieldName: string, values: any[]): void {
    const formArray = this.profileForm.get(fieldName) as FormArray;
    formArray.clear();
    values.forEach(value => {
      if (typeof value === 'string') {
        formArray.push(this.formBuilder.control(value));
      } else {
        formArray.push(this.formBuilder.group(value));
      }
    });
  }

  // Array field getters
  get technicalSkills(): FormArray {
    return this.profileForm.get('technical_skills') as FormArray;
  }

  get achievements(): FormArray {
    return this.profileForm.get('achievements') as FormArray;
  }

  get certifications(): FormArray {
    return this.profileForm.get('certifications') as FormArray;
  }

  get publications(): FormArray {
    return this.profileForm.get('publications') as FormArray;
  }

  get pastCompanies(): FormArray {
    return this.profileForm.get('past_companies') as FormArray;
  }

  get education(): FormArray {
    return this.profileForm.get('education') as FormArray;
  }

  // Array manipulation methods
  addSkill(): void {
    this.technicalSkills.push(this.formBuilder.control(''));
  }

  removeSkill(index: number): void {
    this.technicalSkills.removeAt(index);
  }

  addAchievement(): void {
    this.achievements.push(this.formBuilder.control(''));
  }

  removeAchievement(index: number): void {
    this.achievements.removeAt(index);
  }

  addCertification(): void {
    this.certifications.push(this.formBuilder.control(''));
  }

  removeCertification(index: number): void {
    this.certifications.removeAt(index);
  }

  addPublication(): void {
    this.publications.push(this.formBuilder.control(''));
  }

  removePublication(index: number): void {
    this.publications.removeAt(index);
  }

  addCompany(): void {
    this.pastCompanies.push(this.formBuilder.group({
      name: [''],
      position: [''],
      duration: ['']
    }));
  }

  removeCompany(index: number): void {
    this.pastCompanies.removeAt(index);
  }

  addEducation(): void {
    this.education.push(this.formBuilder.group({
      institution: [''],
      degree: [''],
      field_of_study: [''],
      graduation_year: ['']
    }));
  }

  removeEducation(index: number): void {
    this.education.removeAt(index);
  }

  async onSubmit(): Promise<void> {
    if (this.profileForm.valid && !this.isSaving) {
      try {
        this.isSaving = true;
        const formValue = this.profileForm.value;
        
        // Filter out empty values from arrays
        formValue.technical_skills = formValue.technical_skills.filter((skill: string) => skill.trim());
        formValue.achievements = formValue.achievements.filter((achievement: string) => achievement.trim());
        formValue.certifications = formValue.certifications.filter((cert: string) => cert.trim());
        formValue.publications = formValue.publications.filter((pub: string) => pub.trim());

        this.apiService.updateMyProfile(formValue).subscribe({
          next: (updatedProfile) => {
            this.userProfile = updatedProfile;
            this.showSuccess('Profile updated successfully!');
          },
          error: (error) => {
            console.error('Error updating profile:', error);
            this.showError('Failed to update profile');
          },
          complete: () => {
            this.isSaving = false;
          }
        });
      } catch (error) {
        console.error('Error updating profile:', error);
        this.showError('Failed to update profile');
        this.isSaving = false;
      }
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
}
