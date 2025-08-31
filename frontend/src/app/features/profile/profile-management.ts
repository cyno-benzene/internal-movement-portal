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
      years_experience: [0, [Validators.min(0), Validators.max(50)]],
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
          console.log('Loaded profile:', profile); // Debug log
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

    // Populate arrays with proper fallbacks
    this.setArrayField('technical_skills', this.ensureArray(profile.technical_skills));
    this.setArrayField('achievements', this.ensureArray(profile.achievements));
    this.setArrayField('certifications', this.ensureArray(profile.certifications));
    this.setArrayField('publications', this.ensureArray(profile.publications));
    this.setArrayField('past_companies', this.ensureArray(profile.past_companies));
    this.setArrayField('education', this.ensureArray(profile.education));
  }

  private ensureArray(value: any): any[] {
    if (Array.isArray(value)) {
      return value;
    } else if (value === null || value === undefined) {
      return [];
    } else {
      // If it's a single value, wrap it in an array
      return [value];
    }
  }

  private setArrayField(fieldName: string, values: any[]): void {
    const formArray = this.profileForm.get(fieldName) as FormArray;
    formArray.clear();
    
    console.log(`Setting ${fieldName}:`, values); // Debug log
    
    values.forEach(value => {
      if (fieldName === 'past_companies') {
        // Handle past_companies - can be string or object
        if (typeof value === 'string') {
          // Convert string to object format
          formArray.push(this.formBuilder.group({
            name: [value],
            position: [''],
            duration: ['']
          }));
        } else if (value && typeof value === 'object') {
          formArray.push(this.formBuilder.group({
            name: [value.name || ''],
            position: [value.position || ''],
            duration: [value.duration || '']
          }));
        }
      } else if (fieldName === 'education') {
        // Handle education - can be string or object
        if (typeof value === 'string') {
          // Convert string to object format
          formArray.push(this.formBuilder.group({
            institution: [value],
            degree: [''],
            field_of_study: [''],
            graduation_year: ['']
          }));
        } else if (value && typeof value === 'object') {
          formArray.push(this.formBuilder.group({
            institution: [value.institution || ''],
            degree: [value.degree || ''],
            field_of_study: [value.field_of_study || ''],
            graduation_year: [value.graduation_year || '']
          }));
        }
      } else {
        // Handle simple string arrays (technical_skills, achievements, etc.)
        if (typeof value === 'string') {
          formArray.push(this.formBuilder.control(value));
        } else {
          formArray.push(this.formBuilder.control(value || ''));
        }
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
      name: ['', Validators.required],
      position: [''],
      duration: ['']
    }));
  }

  removeCompany(index: number): void {
    this.pastCompanies.removeAt(index);
  }

  addEducation(): void {
    this.education.push(this.formBuilder.group({
      institution: ['', Validators.required],
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
        
        // Filter out empty values from simple string arrays
        formValue.technical_skills = formValue.technical_skills.filter((skill: string) => skill && skill.trim());
        formValue.achievements = formValue.achievements.filter((achievement: string) => achievement && achievement.trim());
        formValue.certifications = formValue.certifications.filter((cert: string) => cert && cert.trim());
        formValue.publications = formValue.publications.filter((pub: string) => pub && pub.trim());

        // Handle past_companies - convert to backend format
        if (formValue.past_companies) {
          formValue.past_companies = formValue.past_companies
            .filter((company: any) => company && (company.name || company.position || company.duration))
            .map((company: any) => {
              // If all fields are filled, send as object, otherwise send as string (company name)
              if (company.position || company.duration) {
                return {
                  name: company.name || '',
                  position: company.position || '',
                  duration: company.duration || ''
                };
              } else {
                return company.name || '';
              }
            });
        }

        // Handle education - convert to backend format  
        if (formValue.education) {
          formValue.education = formValue.education
            .filter((edu: any) => edu && (edu.institution || edu.degree || edu.field_of_study || edu.graduation_year))
            .map((edu: any) => {
              // If all fields are filled, send as object, otherwise send as string (institution name)
              if (edu.degree || edu.field_of_study || edu.graduation_year) {
                return {
                  institution: edu.institution || '',
                  degree: edu.degree || '',
                  field_of_study: edu.field_of_study || '',
                  graduation_year: edu.graduation_year || ''
                };
              } else {
                return edu.institution || '';
              }
            });
        }

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

  // Helper method to safely get form control values
  getFormControlValue(controlName: string): any {
    const control = this.profileForm.get(controlName);
    return control ? control.value : null;
  }

  // Helper method to check if a form array has valid entries
  hasValidEntries(arrayName: string): boolean {
    const formArray = this.profileForm.get(arrayName) as FormArray;
    return formArray && formArray.length > 0;
  }
}
