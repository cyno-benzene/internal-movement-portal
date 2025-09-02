import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { 
  EmployeeProfile, 
  EmployeeProfileUpdate, 
  WorkExperience, 
  WorkExperienceCreate, 
  WorkExperienceUpdate 
} from '../models/user.model';

@Injectable({
  providedIn: 'root'
})
export class ProfileService {
  private baseUrl = 'http://localhost:8000/api/v1/profiles';

  constructor(private http: HttpClient) {}

  // Profile Management
  getMyProfile(): Observable<EmployeeProfile> {
    return this.http.get<EmployeeProfile>(`${this.baseUrl}/me`);
  }

  updateMyProfile(profileData: EmployeeProfileUpdate): Observable<EmployeeProfile> {
    return this.http.put<EmployeeProfile>(`${this.baseUrl}/me`, profileData);
  }

  getProfile(userId: string): Observable<EmployeeProfile> {
    return this.http.get<EmployeeProfile>(`${this.baseUrl}/${userId}`);
  }

  // Work Experience Management
  getMyWorkExperiences(): Observable<WorkExperience[]> {
    return this.http.get<WorkExperience[]>(`${this.baseUrl}/me/work-experiences`);
  }

  addWorkExperience(workExpData: WorkExperienceCreate): Observable<WorkExperience> {
    return this.http.post<WorkExperience>(`${this.baseUrl}/me/work-experiences`, workExpData);
  }

  updateWorkExperience(workExpId: number, workExpData: WorkExperienceUpdate): Observable<WorkExperience> {
    return this.http.put<WorkExperience>(`${this.baseUrl}/me/work-experiences/${workExpId}`, workExpData);
  }

  deleteWorkExperience(workExpId: number): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/me/work-experiences/${workExpId}`);
  }

  // Manager/HR functionality
  getDirectReports(managerId: string): Observable<EmployeeProfile[]> {
    return this.http.get<EmployeeProfile[]>(`${this.baseUrl}/manager/${managerId}/direct-reports`);
  }

  // Utility methods for experience calculations
  calculateTotalExperienceYears(profile: EmployeeProfile): number {
    return Math.round((profile.months_experience || 0) / 12 * 10) / 10; // Round to 1 decimal
  }

  calculateCompanyTenureYears(profile: EmployeeProfile): number {
    return Math.round((profile.months || 0) / 12 * 10) / 10; // Round to 1 decimal
  }

  formatDuration(months: number): string {
    if (months < 12) {
      return `${months} month${months !== 1 ? 's' : ''}`;
    }
    
    const years = Math.floor(months / 12);
    const remainingMonths = months % 12;
    
    if (remainingMonths === 0) {
      return `${years} year${years !== 1 ? 's' : ''}`;
    }
    
    return `${years} year${years !== 1 ? 's' : ''} ${remainingMonths} month${remainingMonths !== 1 ? 's' : ''}`;
  }

  formatWorkExperienceDates(workExp: WorkExperience): string {
    const startDate = new Date(workExp.start_date);
    const endDate = workExp.end_date ? new Date(workExp.end_date) : null;
    
    const formatMonth = (date: Date) => 
      date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
    
    const start = formatMonth(startDate);
    const end = endDate ? formatMonth(endDate) : 'Present';
    
    return `${start} - ${end}`;
  }

  getEmploymentTypeLabel(type?: string): string {
    const labels: { [key: string]: string } = {
      'full-time': 'Full-time',
      'part-time': 'Part-time',
      'contract': 'Contract',
      'internship': 'Internship',
      'freelance': 'Freelance',
      'temporary': 'Temporary'
    };
    
    return labels[type?.toLowerCase() || ''] || type || 'Not specified';
  }

  sortWorkExperiencesByDate(workExperiences: WorkExperience[]): WorkExperience[] {
    return [...workExperiences].sort((a, b) => {
      // Current positions first
      if (a.is_current && !b.is_current) return -1;
      if (!a.is_current && b.is_current) return 1;
      
      // Then by start date (most recent first)
      return new Date(b.start_date).getTime() - new Date(a.start_date).getTime();
    });
  }
}
