from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, date


class WorkExperienceCreate(BaseModel):
    company_name: str
    job_title: str
    start_date: date
    end_date: Optional[date] = None
    is_current: bool = False
    description: Optional[str] = None
    key_achievements: Optional[List[str]] = []
    skills_used: Optional[List[str]] = []
    technologies_used: Optional[List[str]] = []
    location: Optional[str] = None
    employment_type: Optional[str] = None


class WorkExperienceUpdate(BaseModel):
    company_name: Optional[str] = None
    job_title: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_current: Optional[bool] = None
    description: Optional[str] = None
    key_achievements: Optional[List[str]] = None
    skills_used: Optional[List[str]] = None
    technologies_used: Optional[List[str]] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None


class WorkExperienceResponse(BaseModel):
    id: int
    employee_id: str
    company_name: str
    job_title: str
    start_date: date
    end_date: Optional[date] = None
    is_current: bool
    description: Optional[str] = None
    key_achievements: Optional[List[str]] = []
    skills_used: Optional[List[str]] = []
    technologies_used: Optional[List[str]] = []
    location: Optional[str] = None
    employment_type: Optional[str] = None
    duration_months: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class EmployeeProfileUpdate(BaseModel):
    name: Optional[str] = None
    technical_skills: Optional[List[str]] = None
    achievements: Optional[List[str]] = None
    months_experience: Optional[int] = None  # Changed from years_experience
    past_companies: Optional[List[Union[str, Dict[str, Any]]]] = None
    work_experiences: Optional[List[WorkExperienceCreate]] = None
    certifications: Optional[List[str]] = None
    education: Optional[List[Union[str, Dict[str, Any]]]] = None
    publications: Optional[List[str]] = None
    career_aspirations: Optional[str] = None
    location: Optional[str] = None
    current_job_title: Optional[str] = None
    preferred_roles: Optional[List[str]] = None
    visibility_opt_out: Optional[bool] = None
    
    # New enhanced profile fields
    date_of_joining: Optional[date] = None
    reporting_officer_id: Optional[str] = None
    rep_officer_name: Optional[str] = None

class EmployeeProfileResponse(BaseModel):
    id: str
    employee_id: str
    email: str
    name: str
    role: str
    technical_skills: Optional[List[str]] = []
    achievements: Optional[List[str]] = []
    months_experience: Optional[int] = 0  # Changed from years_experience
    past_companies: Optional[List[Any]] = []  # Can be strings or dicts for flexibility
    certifications: Optional[List[str]] = []
    education: Optional[List[Any]] = []  # Can be strings or dicts for flexibility
    publications: Optional[List[str]] = []
    career_aspirations: Optional[str] = None
    location: Optional[str] = None
    current_job_title: Optional[str] = None
    preferred_roles: Optional[List[str]] = []
    visibility_opt_out: Optional[bool] = False
    parsed_resume: Optional[Dict[str, Any]] = None
    
    # New enhanced profile fields
    date_of_joining: Optional[date] = None
    reporting_officer_id: Optional[str] = None
    rep_officer_name: Optional[str] = None
    months: Optional[int] = 0  # Time in company
    
    # Work experiences (will be populated via relationship)
    work_experiences: Optional[List[WorkExperienceResponse]] = []
    
    updated_at: datetime
    
    class Config:
        from_attributes = True

class EmployeeResponse(BaseModel):
    """Simplified employee response for discovery/search"""
    id: str
    employee_id: str
    name: str
    email: str
    role: str
    technical_skills: Optional[List[str]] = []
    months_experience: Optional[int] = 0  # Changed from years_experience
    current_job_title: Optional[str] = None
    preferred_roles: Optional[List[str]] = []
    certifications: Optional[List[str]] = []
    location: Optional[str]
    
    # New enhanced fields for discovery
    date_of_joining: Optional[date] = None
    months: Optional[int] = 0  # Time in company
    rep_officer_name: Optional[str] = None
    
    class Config:
        from_attributes = True

class RoleUpdateRequest(BaseModel):
    role: str