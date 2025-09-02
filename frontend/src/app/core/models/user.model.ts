export interface User {
  id: string;
  employee_id: string;
  email: string;
  name: string;
  role: 'employee' | 'manager' | 'hr' | 'admin';
}

export interface LoginRequest {
  employee_id: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user_id: string;
  employee_id: string;
  email: string;
  role: string;
  name: string;
}

export interface WorkExperience {
  id: number;
  employee_id: string;
  company_name: string;
  job_title: string;
  start_date: string; // ISO date string
  end_date?: string; // ISO date string
  is_current: boolean;
  description?: string;
  key_achievements: string[];
  skills_used: string[];
  technologies_used: string[];
  location?: string;
  employment_type?: string;
  duration_months?: number;
  created_at: string;
  updated_at?: string;
}

export interface WorkExperienceCreate {
  company_name: string;
  job_title: string;
  start_date: string; // ISO date string
  end_date?: string; // ISO date string
  is_current: boolean;
  description?: string;
  key_achievements?: string[];
  skills_used?: string[];
  technologies_used?: string[];
  location?: string;
  employment_type?: string;
}

export interface WorkExperienceUpdate {
  company_name?: string;
  job_title?: string;
  start_date?: string; // ISO date string
  end_date?: string; // ISO date string
  is_current?: boolean;
  description?: string;
  key_achievements?: string[];
  skills_used?: string[];
  technologies_used?: string[];
  location?: string;
  employment_type?: string;
}

export interface EmployeeProfile {
  id: string;
  employee_id: string;
  email: string;
  name: string;
  role: string;
  technical_skills: string[];
  achievements: string[];
  months_experience: number; // Changed from years_experience
  past_companies: any[];
  certifications: string[];
  education: any[];
  publications: string[];
  career_aspirations?: string;
  location?: string;
  current_job_title?: string;
  preferred_roles: string[];
  visibility_opt_out: boolean;
  parsed_resume?: any;
  
  // New enhanced profile fields
  date_of_joining?: string; // ISO date string
  reporting_officer_id?: string;
  rep_officer_name?: string;
  months?: number; // Time in company
  
  // Work experiences
  work_experiences: WorkExperience[];
  
  updated_at: string;
}

export interface EmployeeProfileUpdate {
  name?: string;
  technical_skills?: string[];
  achievements?: string[];
  months_experience?: number; // Changed from years_experience
  past_companies?: any[];
  certifications?: string[];
  education?: any[];
  publications?: string[];
  career_aspirations?: string;
  location?: string;
  current_job_title?: string;
  preferred_roles?: string[];
  visibility_opt_out?: boolean;
  
  // New enhanced profile fields
  date_of_joining?: string; // ISO date string
  reporting_officer_id?: string;
  rep_officer_name?: string;
}
