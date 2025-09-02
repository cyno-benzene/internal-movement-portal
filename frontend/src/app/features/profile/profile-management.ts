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
import { MatTabsModule } from '@angular/material/tabs';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatDividerModule } from '@angular/material/divider';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { RouterModule } from '@angular/router';
import { ProfileService } from '../../core/services/profile';
import { AuthService } from '../../core/services/auth';
import { EmployeeProfile, WorkExperience, WorkExperienceCreate, WorkExperienceUpdate } from '../../core/models/user.model';

@Component({
  selector: 'app-profile-management',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    RouterModule,
    MatCardModule,
    MatButtonModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatChipsModule,
    MatIconModule,
    MatSnackBarModule,
    MatTabsModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatCheckboxModule,
    MatExpansionModule,
    MatDividerModule,
    MatProgressSpinnerModule
  ],
  templateUrl: './profile-management.html',
  styleUrls: ['./profile-management.scss']
})
export class ProfileManagementComponent implements OnInit {
  profileForm!: FormGroup;
  workExperienceForm!: FormGroup;
  userProfile: EmployeeProfile | null = null;
  workExperiences: WorkExperience[] = [];
  isLoading = true;
  isSaving = false;
  isAddingWorkExp = false;
  editingWorkExpId: number | null = null;
  isEditMode = false;

  employmentTypes = [
    { value: 'full-time', label: 'Full-time' },
    { value: 'part-time', label: 'Part-time' },
    { value: 'contract', label: 'Contract' },
    { value: 'internship', label: 'Internship' },
    { value: 'freelance', label: 'Freelance' },
    { value: 'temporary', label: 'Temporary' }
  ];

  months = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  years: number[] = [];

  constructor(
    private formBuilder: FormBuilder,
    private profileService: ProfileService,
    private authService: AuthService,
    private snackBar: MatSnackBar
  ) {
    this.initializeYears();
    this.initializeForms();
  }

  ngOnInit(): void {
    this.loadUserProfile();
  }

  private initializeYears(): void {
    const currentYear = new Date().getFullYear();
    const startYear = currentYear - 50; // Allow up to 50 years of experience
    this.years = [];
    for (let year = currentYear; year >= startYear; year--) {
      this.years.push(year);
    }
  }

  private initializeForms(): void {
        // Initialize reactive form
    this.profileForm = this.formBuilder.group({
      full_name: ['', [Validators.required]],
      email: ['', [Validators.required, Validators.email]],
      phone: [''],
      department: [''],
      team: [''],
      years_experience: [0],
      months_experience: [0],
      technical_skills: this.formBuilder.array([]),
      achievements: this.formBuilder.array([]),
      education: this.formBuilder.array([]),
      certifications: this.formBuilder.array([]),
      publications: this.formBuilder.array([]),
      past_companies: this.formBuilder.array([]),
      work_experiences: this.formBuilder.array([]),
      career_aspirations: [''],
      bio: [''],
      location: [''],
      current_job_title: [''],
      preferred_roles: this.formBuilder.array([]),
      date_of_joining: [''],
      reporting_officer_id: [''],
      rep_officer_name: ['']
    });

    // Work experience form
    this.workExperienceForm = this.formBuilder.group({
      company_name: ['', [Validators.required]],
      job_title: ['', [Validators.required]],
      start_date: ['', [Validators.required]],
      end_date: [''],
      is_current: [false],
      description: [''],
      key_achievements: this.formBuilder.array([]),
      skills_used: this.formBuilder.array([]),
      technologies_used: this.formBuilder.array([]),
      location: [''],
      employment_type: ['full-time']
    });

    // Watch is_current checkbox to clear end_date when checked
    this.workExperienceForm.get('is_current')?.valueChanges.subscribe(isCurrent => {
      if (isCurrent) {
        this.workExperienceForm.get('end_date')?.setValue('');
        this.workExperienceForm.get('end_date')?.clearValidators();
      } else {
        this.workExperienceForm.get('end_date')?.setValidators([Validators.required]);
      }
      this.workExperienceForm.get('end_date')?.updateValueAndValidity();
    });
  }

  private async loadUserProfile(): Promise<void> {
    try {
      this.isLoading = true;
      this.profileService.getMyProfile().subscribe({
        next: (profile: EmployeeProfile) => {
          console.log('Loaded profile:', profile);
          this.userProfile = profile;
          this.workExperiences = this.profileService.sortWorkExperiencesByDate(profile.work_experiences || []);
          this.populateForm(profile);
        },
        error: (error: any) => {
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
      full_name: profile.name,
      email: profile.email || '',
      months_experience: profile.months_experience || 0,
      career_aspirations: profile.career_aspirations || '',
      location: profile.location || '',
      current_job_title: profile.current_job_title || '',
      date_of_joining: profile.date_of_joining || '',
      reporting_officer_id: profile.reporting_officer_id || '',
      rep_officer_name: profile.rep_officer_name || ''
    });

    // Populate arrays with proper fallbacks
    this.setArrayField('technical_skills', this.ensureArray(profile.technical_skills));
    this.setArrayField('achievements', this.ensureArray(profile.achievements));
    this.setArrayField('certifications', this.ensureArray(profile.certifications));
    this.setArrayField('publications', this.ensureArray(profile.publications));
    this.setArrayField('past_companies', this.ensureArray(profile.past_companies));
    this.setArrayField('preferred_roles', this.ensureArray(profile.preferred_roles));
    this.setArrayField('education', this.ensureArray(profile.education));
    this.setArrayField('work_experiences', this.ensureArray(profile.work_experiences));
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
    
    if (!formArray) {
      console.warn(`FormArray '${fieldName}' not found in form`);
      return;
    }
    
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
            field: [''],
            year: ['']
          }));
        } else if (value && typeof value === 'object') {
          formArray.push(this.formBuilder.group({
            institution: [value.institution || ''],
            degree: [value.degree || ''],
            field: [value.field || value.field_of_study || ''],
            year: [value.year || value.graduation_year || '']
          }));
        }
      } else if (fieldName === 'work_experiences') {
        // Handle work_experiences - convert dates to month/year
        if (value && typeof value === 'object') {
          const startDate = value.start_date ? new Date(value.start_date) : null;
          const endDate = value.end_date ? new Date(value.end_date) : null;
          
          formArray.push(this.formBuilder.group({
            company_name: [value.company_name || '', Validators.required],
            job_title: [value.job_title || '', Validators.required],
            employment_type: [value.employment_type || 'full-time'],
            start_month: [startDate ? startDate.getMonth() + 1 : '', Validators.required],
            start_year: [startDate ? startDate.getFullYear() : '', Validators.required],
            end_month: [endDate ? endDate.getMonth() + 1 : '', Validators.required],
            end_year: [endDate ? endDate.getFullYear() : '', Validators.required],
            description: [value.description || ''],
            location: [value.location || '']
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

  get workExperienceArray(): FormArray {
    return this.profileForm.get('work_experiences') as FormArray;
  }

  get education(): FormArray {
    return this.profileForm.get('education') as FormArray;
  }

  get preferredRoles(): FormArray {
    return this.profileForm.get('preferred_roles') as FormArray;
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

  // New work experience methods
  addWorkExperience(): void {
    this.workExperienceArray.push(this.formBuilder.group({
      company_name: ['', Validators.required],
      job_title: ['', Validators.required],
      employment_type: ['full-time'],
      start_month: ['', Validators.required],
      start_year: ['', Validators.required],
      end_month: ['', Validators.required],
      end_year: ['', Validators.required],
      description: [''],
      location: ['']
    }));
  }

  removeWorkExperience(index: number): void {
    this.workExperienceArray.removeAt(index);
  }

  // Calculate duration from month/year values
  calculateDuration(startMonth: number, startYear: number, endMonth?: number, endYear?: number): number {
    const currentDate = new Date();
    const currentMonth = currentDate.getMonth() + 1; // getMonth() returns 0-11
    const currentYear = currentDate.getFullYear();
    
    const actualEndMonth = endMonth || currentMonth;
    const actualEndYear = endYear || currentYear;
    
    const months = (actualEndYear - startYear) * 12 + (actualEndMonth - startMonth);
    return Math.max(0, months);
  }

  // Helper method for template - works with work experience object
  calculateExperienceDuration(exp: any): number {
    // Handle both date strings (from backend) and month/year values (from form)
    if (exp.start_date) {
      // Backend data - dates as strings
      const startDate = new Date(exp.start_date);
      const endDate = exp.end_date ? new Date(exp.end_date) : new Date();
      
      const months = (endDate.getFullYear() - startDate.getFullYear()) * 12 + 
                     (endDate.getMonth() - startDate.getMonth());
      return Math.max(0, months);
    } else if (exp.start_month && exp.start_year) {
      // Form data - separate month/year values
      const duration = this.calculateDuration(
        exp.start_month, 
        exp.start_year,
        exp.end_month,
        exp.end_year
      );
      return duration;
    }
    
    return 0;
  }

  addEducation(): void {
    this.education.push(this.formBuilder.group({
      institution: ['', Validators.required],
      degree: [''],
      field: [''],
      year: ['']
    }));
  }

  removeEducation(index: number): void {
    this.education.removeAt(index);
  }

  addPreferredRole(): void {
    this.preferredRoles.push(this.formBuilder.control(''));
  }

  removePreferredRole(index: number): void {
    this.preferredRoles.removeAt(index);
  }

  // Edit mode methods
  enableEditMode(): void {
    this.isEditMode = true;
  }

  cancelEdit(): void {
    this.isEditMode = false;
    // Reload the profile to reset any unsaved changes
    if (this.userProfile) {
      this.populateForm(this.userProfile);
    }
  }

  async onSubmit(): Promise<void> {
    if (this.profileForm.valid && !this.isSaving) {
      try {
        this.isSaving = true;
        const formValue = this.profileForm.value;
        
        // Handle empty date fields - convert empty strings to null
        if (formValue.date_of_joining === '') {
          formValue.date_of_joining = null;
        }
        
        // Handle other fields that should be null if empty
        if (formValue.reporting_officer_id === '') {
          formValue.reporting_officer_id = null;
        }
        if (formValue.rep_officer_name === '') {
          formValue.rep_officer_name = null;
        }
        if (formValue.career_aspirations === '') {
          formValue.career_aspirations = null;
        }
        if (formValue.location === '') {
          formValue.location = null;
        }
        if (formValue.current_job_title === '') {
          formValue.current_job_title = null;
        }
        
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

        // Handle work_experiences - convert month/year to dates and calculate duration
        if (formValue.work_experiences) {
          formValue.work_experiences = formValue.work_experiences
            .filter((exp: any) => exp && exp.company_name && exp.job_title && exp.start_month && exp.start_year)
            .map((exp: any) => {
              // Convert month/year to dates (consistent approach)
              // Start date: First day of the month
              const startDate = new Date(exp.start_year, exp.start_month - 1, 1);
              let endDate = null;
              let durationMonths = 0;
              
              if (exp.end_month && exp.end_year) {
                // End date: Last day of the month to ensure proper month counting
                endDate = new Date(exp.end_year, exp.end_month, 0); // Day 0 = last day of previous month
                durationMonths = this.calculateDuration(exp.start_month, exp.start_year, exp.end_month, exp.end_year);
              } else {
                // Current position - calculate duration to now
                durationMonths = this.calculateDuration(exp.start_month, exp.start_year);
              }

              return {
                company_name: exp.company_name,
                job_title: exp.job_title,
                employment_type: exp.employment_type || 'full-time',
                start_date: startDate.toISOString().split('T')[0], // YYYY-MM-DD format
                end_date: endDate ? endDate.toISOString().split('T')[0] : null,
                is_current: !endDate, // If no end date, it's current
                description: exp.description || '',
                location: exp.location || '',
                duration_months: durationMonths
              };
            });
        }

        // Handle education - convert to backend format  
        if (formValue.education) {
          formValue.education = formValue.education
            .filter((edu: any) => edu && (edu.institution || edu.degree || edu.field || edu.year))
            .map((edu: any) => {
              // If all fields are filled, send as object, otherwise send as string (institution name)
              if (edu.degree || edu.field || edu.year) {
                return {
                  institution: edu.institution || '',
                  degree: edu.degree || '',
                  field_of_study: edu.field || '', // Map field to field_of_study for backend
                  graduation_year: edu.year || '' // Map year to graduation_year for backend
                };
              } else {
                return edu.institution || '';
              }
            });
        }

        this.profileService.updateMyProfile(formValue).subscribe({
          next: (updatedProfile: EmployeeProfile) => {
            this.userProfile = updatedProfile;
            // Update work experiences array for immediate display
            this.workExperiences = this.profileService.sortWorkExperiencesByDate(updatedProfile.work_experiences || []);
            this.showSuccess('Profile updated successfully!');
            this.isEditMode = false; // Exit edit mode on successful save
          },
          error: (error: any) => {
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

  // Work Experience Management Methods
  
  startAddingWorkExperience(): void {
    this.isAddingWorkExp = true;
    this.editingWorkExpId = null;
    this.workExperienceForm.reset({
      is_current: false,
      employment_type: 'full-time'
    });
    this.resetWorkExpArrays();
  }

  editWorkExperience(workExp: WorkExperience): void {
    this.isAddingWorkExp = true;
    this.editingWorkExpId = workExp.id;
    
    this.workExperienceForm.patchValue({
      company_name: workExp.company_name,
      job_title: workExp.job_title,
      start_date: workExp.start_date,
      end_date: workExp.end_date || '',
      is_current: workExp.is_current,
      description: workExp.description || '',
      location: workExp.location || '',
      employment_type: workExp.employment_type || 'full-time'
    });

    this.setWorkExpArrayField('key_achievements', workExp.key_achievements || []);
    this.setWorkExpArrayField('skills_used', workExp.skills_used || []);
    this.setWorkExpArrayField('technologies_used', workExp.technologies_used || []);
  }

  cancelWorkExperience(): void {
    this.isAddingWorkExp = false;
    this.editingWorkExpId = null;
    this.workExperienceForm.reset();
  }

  async saveWorkExperience(): Promise<void> {
    if (this.workExperienceForm.invalid) {
      this.markFormGroupTouched(this.workExperienceForm);
      return;
    }

    const formValue = this.workExperienceForm.value;
    
    // Convert FormArray values to arrays
    const workExpData = {
      ...formValue,
      key_achievements: this.getArrayFieldValues('key_achievements', this.workExperienceForm),
      skills_used: this.getArrayFieldValues('skills_used', this.workExperienceForm),
      technologies_used: this.getArrayFieldValues('technologies_used', this.workExperienceForm)
    };

    try {
      this.isSaving = true;

      if (this.editingWorkExpId) {
        // Update existing work experience
        this.profileService.updateWorkExperience(this.editingWorkExpId, workExpData).subscribe({
          next: (updatedWorkExp: WorkExperience) => {
            const index = this.workExperiences.findIndex(we => we.id === this.editingWorkExpId);
            if (index !== -1) {
              this.workExperiences[index] = updatedWorkExp;
              this.workExperiences = this.profileService.sortWorkExperiencesByDate(this.workExperiences);
            }
            this.showSuccess('Work experience updated successfully');
            this.cancelWorkExperience();
          },
          error: (error: any) => {
            console.error('Error updating work experience:', error);
            this.showError('Failed to update work experience');
          },
          complete: () => {
            this.isSaving = false;
          }
        });
      } else {
        // Add new work experience
        this.profileService.addWorkExperience(workExpData).subscribe({
          next: (newWorkExp: WorkExperience) => {
            this.workExperiences.push(newWorkExp);
            this.workExperiences = this.profileService.sortWorkExperiencesByDate(this.workExperiences);
            this.showSuccess('Work experience added successfully');
            this.cancelWorkExperience();
          },
          error: (error: any) => {
            console.error('Error adding work experience:', error);
            this.showError('Failed to add work experience');
          },
          complete: () => {
            this.isSaving = false;
          }
        });
      }
    } catch (error) {
      console.error('Error saving work experience:', error);
      this.showError('Failed to save work experience');
      this.isSaving = false;
    }
  }

  async deleteWorkExperience(workExp: WorkExperience): Promise<void> {
    if (!confirm(`Are you sure you want to delete the work experience at ${workExp.company_name}?`)) {
      return;
    }

    try {
      this.profileService.deleteWorkExperience(workExp.id).subscribe({
        next: () => {
          this.workExperiences = this.workExperiences.filter(we => we.id !== workExp.id);
          this.showSuccess('Work experience deleted successfully');
        },
        error: (error: any) => {
          console.error('Error deleting work experience:', error);
          this.showError('Failed to delete work experience');
        }
      });
    } catch (error) {
      console.error('Error deleting work experience:', error);
      this.showError('Failed to delete work experience');
    }
  }

  // Work Experience Form Array Helpers
  get workExpKeyAchievements(): FormArray {
    return this.workExperienceForm.get('key_achievements') as FormArray;
  }

  get workExpSkillsUsed(): FormArray {
    return this.workExperienceForm.get('skills_used') as FormArray;
  }

  get workExpTechnologiesUsed(): FormArray {
    return this.workExperienceForm.get('technologies_used') as FormArray;
  }

  addWorkExpAchievement(): void {
    this.workExpKeyAchievements.push(this.formBuilder.control(''));
  }

  removeWorkExpAchievement(index: number): void {
    this.workExpKeyAchievements.removeAt(index);
  }

  addWorkExpSkill(): void {
    this.workExpSkillsUsed.push(this.formBuilder.control(''));
  }

  removeWorkExpSkill(index: number): void {
    this.workExpSkillsUsed.removeAt(index);
  }

  addWorkExpTechnology(): void {
    this.workExpTechnologiesUsed.push(this.formBuilder.control(''));
  }

  removeWorkExpTechnology(index: number): void {
    this.workExpTechnologiesUsed.removeAt(index);
  }

  private setWorkExpArrayField(fieldName: string, values: string[]): void {
    const formArray = this.workExperienceForm.get(fieldName) as FormArray;
    formArray.clear();
    values.forEach(value => {
      formArray.push(this.formBuilder.control(value));
    });
  }

  private resetWorkExpArrays(): void {
    ['key_achievements', 'skills_used', 'technologies_used'].forEach(fieldName => {
      const formArray = this.workExperienceForm.get(fieldName) as FormArray;
      formArray.clear();
    });
  }

  // Helper method to get array values from form
  private getArrayFieldValues(fieldName: string, form: FormGroup): string[] {
    const formArray = form.get(fieldName) as FormArray;
    return formArray ? formArray.controls.map(control => control.value).filter(value => value.trim() !== '') : [];
  }

  // Utility methods for display
  formatWorkExperienceDates(workExp: WorkExperience): string {
    return this.profileService.formatWorkExperienceDates(workExp);
  }

  formatDuration(months?: number): string {
    return months ? this.profileService.formatDuration(months) : '';
  }

  formatTotalExperience(months: number): string {
    return this.profileService.formatDuration(months);
  }

  getEmploymentTypeLabel(type?: string): string {
    return this.profileService.getEmploymentTypeLabel(type);
  }

  getTotalExperienceYears(): number {
    return this.userProfile ? this.profileService.calculateTotalExperienceYears(this.userProfile) : 0;
  }

  getCompanyTenureYears(): number {
    return this.userProfile ? this.profileService.calculateCompanyTenureYears(this.userProfile) : 0;
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

  // Helper method to mark all fields in a form group as touched
  private markFormGroupTouched(formGroup: FormGroup): void {
    Object.keys(formGroup.controls).forEach(key => {
      const control = formGroup.get(key);
      control?.markAsTouched();
      
      if (control instanceof FormGroup) {
        this.markFormGroupTouched(control);
      } else if (control instanceof FormArray) {
        control.controls.forEach(arrayControl => {
          if (arrayControl instanceof FormGroup) {
            this.markFormGroupTouched(arrayControl);
          } else {
            arrayControl.markAsTouched();
          }
        });
      }
    });
  }
}
