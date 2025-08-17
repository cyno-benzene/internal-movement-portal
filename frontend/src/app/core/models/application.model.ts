import { Job } from './job.model';
import { EmployeeProfile } from './user.model';

export interface Application {
  id: string;
  job_id: string;
  employee_id: string;
  status: string;
  manager_comment?: string;
  hr_comment?: string;
  created_at: string;
  updated_at: string;
}

export interface ApplicationDetail {
  id: string;
  job: Job;
  employee: EmployeeProfile;
  status: string;
  manager_comment?: string;
  hr_comment?: string;
  created_at: string;
  updated_at: string;
}
