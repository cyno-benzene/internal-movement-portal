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

export interface EmployeeProfile {
  id: string;
  email: string;
  name: string;
  role: string;
  technical_skills: string[];
  achievements: string[];
  years_experience: number;
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
  updated_at: string;
}

export interface EmployeeProfileUpdate {
  name?: string;
  technical_skills?: string[];
  achievements?: string[];
  years_experience?: number;
  past_companies?: any[];
  certifications?: string[];
  education?: any[];
  publications?: string[];
  career_aspirations?: string;
  location?: string;
  current_job_title?: string;
  preferred_roles?: string[];
  visibility_opt_out?: boolean;
}
