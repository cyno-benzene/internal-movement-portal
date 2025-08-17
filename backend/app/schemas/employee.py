from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime

class EmployeeProfileUpdate(BaseModel):
    name: Optional[str] = None
    technical_skills: Optional[List[str]] = None
    achievements: Optional[List[str]] = None
    years_experience: Optional[int] = None
    past_companies: Optional[List[Dict[str, Any]]] = None
    certifications: Optional[List[str]] = None
    education: Optional[List[Dict[str, Any]]] = None
    publications: Optional[List[str]] = None
    career_aspirations: Optional[str] = None
    location: Optional[str] = None
    visibility_opt_out: Optional[bool] = None

class EmployeeProfileResponse(BaseModel):
    id: str
    employee_id: str
    email: str
    name: str
    role: str
    technical_skills: Optional[List[str]] = []
    achievements: Optional[List[str]] = []
    years_experience: Optional[int] = 0
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
    years_experience: Optional[int] = 0
    current_job_title: Optional[str] = None
    preferred_roles: Optional[List[str]] = []
    certifications: Optional[List[str]] = []
    location: Optional[str]
    
    class Config:
        from_attributes = True

class RoleUpdateRequest(BaseModel):
    role: str