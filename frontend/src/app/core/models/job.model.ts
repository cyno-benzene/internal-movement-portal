export interface Job {
  id: string;
  title: string;
  team: string;
  description: string;
  short_description?: string;
  required_skills: string[];
  optional_skills?: string[];
  min_years_experience?: number;
  preferred_certifications?: string[];
  status: string;
  visibility: 'open' | 'invite_only';
  internal_notes?: string;
  manager_id: string;
  manager_name?: string;
  created_at: string;
}

export interface JobCreate {
  title: string;
  team: string;
  description: string;
  short_description?: string;
  required_skills: string[];
  optional_skills?: string[];
  min_years_experience?: number;
  preferred_certifications?: string[];
  visibility?: 'open' | 'invite_only';
  internal_notes?: string;
}

export interface JobMatch {
  job: {
    id: string;
    title: string;
    team: string;
    short_description?: string;
    manager_name?: string;
  };
  score: number;
  reasoning?: string;
}

export interface Invitation {
  id: string;
  job: {
    id: string;
    title: string;
    team: string;
    short_description: string;
    manager_name: string;
    department?: string;
    location?: string;
    description?: string;
    employment_type?: string;
    salary_range?: string;
    created_at?: string;
    required_skills?: string[];
  };
  employee: {
    id: string;
    name: string;
    email: string;
    role: string;
    full_name?: string;
  };
  inviter: {
    id: string;
    name: string;
    email: string;
    role: string;
    full_name?: string;
    current_job_title?: string;
  };
  status: 'pending' | 'accepted' | 'declined';
  created_at: string;
  personal_message?: string;
  responded_at?: string;
  employee_response_reason?: string;
}

export interface InvitationResponse {
  decision: 'accept' | 'decline' | 'request_info';
  note?: string;
}

export interface EmployeeCandidate {
  id: string;
  employee_id: string;
  name: string;
  email: string;
  role: string;
  technical_skills: string[];
  years_experience: number;
  current_job_title?: string;
  preferred_roles: string[];
  certifications: string[];
  location?: string;
}
