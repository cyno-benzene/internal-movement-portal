import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { Job, JobCreate, JobMatch, Invitation, EmployeeCandidate } from '../models/job.model';
import { JobComment, JobCommentCreate } from '../models/job-comment.model';
import { Application, ApplicationDetail } from '../models/application.model';
import { EmployeeProfile, User } from '../models/user.model';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  constructor(private http: HttpClient) {}

  // Jobs
  getJobs(): Observable<Job[]> {
    return this.http.get<Job[]>(`${environment.apiUrl}/jobs/`);
  }

  getJob(id: string): Observable<Job> {
    return this.http.get<Job>(`${environment.apiUrl}/jobs/${id}`);
  }

  createJob(job: JobCreate): Observable<Job> {
    return this.http.post<Job>(`${environment.apiUrl}/jobs/`, job);
  }

  updateJob(id: string, job: Partial<JobCreate>): Observable<Job> {
    return this.http.put<Job>(`${environment.apiUrl}/jobs/${id}`, job);
  }

  deleteJob(id: string): Observable<void> {
    return this.http.delete<void>(`${environment.apiUrl}/jobs/${id}`);
  }

  getJobMatches(jobId: string): Observable<any[]> {
    return this.http.get<any[]>(`${environment.apiUrl}/jobs/${jobId}/matches`);
  }

  // Job Comments
  getJobComments(jobId: string): Observable<JobComment[]> {
    return this.http.get<JobComment[]>(`${environment.apiUrl}/jobs/${jobId}/comments`);
  }

  createJobComment(jobId: string, content: string): Observable<JobComment> {
    return this.http.post<JobComment>(`${environment.apiUrl}/jobs/${jobId}/comments`, { content });
  }

  triggerMatching(jobId: string): Observable<void> {
    return this.http.post<void>(`${environment.apiUrl}/jobs/${jobId}/match`, {});
  }

  // Candidate discovery and invitation workflow
  discoverCandidates(jobId: string): Observable<EmployeeCandidate[]> {
    return this.http.get<EmployeeCandidate[]>(`${environment.apiUrl}/jobs/${jobId}/discover`);
  }

  shortlistCandidate(jobId: string, employeeId: string): Observable<void> {
    return this.http.post<void>(`${environment.apiUrl}/jobs/${jobId}/shortlist`, { employee_id: employeeId });
  }

  removeFromShortlist(jobId: string, employeeId: string): Observable<void> {
    return this.http.delete<void>(`${environment.apiUrl}/jobs/${jobId}/shortlist`, { 
      body: { employee_id: employeeId } 
    });
  }

  inviteCandidate(jobId: string, employeeId: string, personalMessage?: string): Observable<void> {
    return this.http.post<void>(`${environment.apiUrl}/jobs/${jobId}/invite`, { 
      employee_id: employeeId,
      personal_message: personalMessage 
    });
  }

  // Invitations (Employee perspective)
  getMyInvitations(): Observable<Invitation[]> {
    return this.http.get<Invitation[]>(`${environment.apiUrl}/invitations/me`);
  }

  // Invitations (Manager/HR perspective)
  getSentInvitations(): Observable<Invitation[]> {
    return this.http.get<Invitation[]>(`${environment.apiUrl}/invitations/sent`);
  }

  respondToInvitation(invitationId: string, response: 'accepted' | 'declined', reason?: string): Observable<void> {
    return this.http.post<void>(`${environment.apiUrl}/invitations/${invitationId}/respond`, {
      response,
      reason
    });
  }

  // Applications
  getApplications(): Observable<ApplicationDetail[]> {
    return this.http.get<ApplicationDetail[]>(`${environment.apiUrl}/applications/`);
  }

  createApplication(jobId: string): Observable<Application> {
    return this.http.post<Application>(`${environment.apiUrl}/applications/`, { job_id: jobId });
  }

  updateApplication(id: string, update: any): Observable<Application> {
    return this.http.put<Application>(`${environment.apiUrl}/applications/${id}`, update);
  }

  // Profile
  getMyProfile(): Observable<EmployeeProfile> {
    return this.http.get<EmployeeProfile>(`${environment.apiUrl}/profiles/me`);
  }

  updateMyProfile(profile: Partial<EmployeeProfile>): Observable<EmployeeProfile> {
    // Only send fields that are allowed in EmployeeProfileUpdate
    const updateData: any = {};
    
    if (profile.name !== undefined) updateData.name = profile.name;
    if (profile.technical_skills !== undefined) updateData.technical_skills = profile.technical_skills;
    if (profile.achievements !== undefined) updateData.achievements = profile.achievements;
    if (profile.years_experience !== undefined) updateData.years_experience = profile.years_experience;
    if (profile.past_companies !== undefined) updateData.past_companies = profile.past_companies;
    if (profile.certifications !== undefined) updateData.certifications = profile.certifications;
    if (profile.education !== undefined) updateData.education = profile.education;
    if (profile.publications !== undefined) updateData.publications = profile.publications;
    if (profile.career_aspirations !== undefined) updateData.career_aspirations = profile.career_aspirations;
    if (profile.location !== undefined) updateData.location = profile.location;
    if (profile.visibility_opt_out !== undefined) updateData.visibility_opt_out = profile.visibility_opt_out;
    
    return this.http.put<EmployeeProfile>(`${environment.apiUrl}/profiles/me`, updateData);
  }

  updateVisibilityPreference(visibilityOptOut: boolean): Observable<void> {
    return this.http.put<void>(`${environment.apiUrl}/profiles/me/visibility`, { 
      visibility_opt_out: visibilityOptOut 
    });
  }

  getProfile(id: string): Observable<EmployeeProfile> {
    return this.http.get<EmployeeProfile>(`${environment.apiUrl}/profiles/${id}`);
  }

  // Matched jobs for employee
  getMatchedJobs(): Observable<JobMatch[]> {
    return this.http.get<JobMatch[]>(`${environment.apiUrl}/me/matched-jobs`);
  }

  // Admin
  getAllUsers(): Observable<User[]> {
    return this.http.get<User[]>(`${environment.apiUrl}/admin/users`);
  }

  updateUserRole(userId: string, role: string): Observable<User> {
    return this.http.put<User>(`${environment.apiUrl}/admin/users/${userId}/role`, { role });
  }

  reassignJob(jobId: string, newManagerId: string): Observable<void> {
    return this.http.put<void>(`${environment.apiUrl}/admin/jobs/${jobId}/reassign`, { new_manager_id: newManagerId });
  }

  overrideApplicationStatus(applicationId: string, status: string): Observable<void> {
    return this.http.post<void>(`${environment.apiUrl}/admin/applications/${applicationId}/override`, { status });
  }

  // Notifications
  getNotifications(): Observable<any[]> {
    return this.http.get<any[]>(`${environment.apiUrl}/notifications/`);
  }

  markNotificationsRead(notificationIds: string[]): Observable<void> {
    return this.http.post<void>(`${environment.apiUrl}/notifications/mark-read`, { notification_ids: notificationIds });
  }
}
