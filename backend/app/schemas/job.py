from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class JobCreate(BaseModel):
    title: str
    team: str
    description: str
    note: Optional[str] = None
    required_skills: List[str]
    optional_skills: Optional[List[str]] = None
    min_years_experience: Optional[int] = 0
    preferred_certifications: Optional[List[str]] = None
    priority: Optional[str] = "normal"  # normal, high_importance

class JobUpdate(BaseModel):
    title: Optional[str] = None
    team: Optional[str] = None
    description: Optional[str] = None
    note: Optional[str] = None
    required_skills: Optional[List[str]] = None
    optional_skills: Optional[List[str]] = None
    min_years_experience: Optional[int] = None
    preferred_certifications: Optional[List[str]] = None
    priority: Optional[str] = None  # normal, high_importance
    status: Optional[str] = None

class JobResponse(BaseModel):
    id: str
    title: str
    team: str
    description: str
    note: Optional[str] = None
    required_skills: List[str] = []
    optional_skills: Optional[List[str]] = []
    min_years_experience: Optional[int] = 0
    preferred_certifications: Optional[List[str]] = []
    priority: Optional[str] = "normal"  # normal, high_importance
    status: str
    matching_status: Optional[str] = "not_matched"  # not_matched, matching, matched
    manager_id: str
    manager_name: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class JobMatchResponse(BaseModel):
    employee_id: str
    employee_name: str
    employee_email: str
    score: int
    skills_match: List[str] = []
    
    class Config:
        from_attributes = True

class EmployeeJobMatchResponse(BaseModel):
    job: JobResponse
    score: int
    
    class Config:
        from_attributes = True
