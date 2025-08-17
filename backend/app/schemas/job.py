from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class JobCreate(BaseModel):
    title: str
    team: str
    description: str
    short_description: Optional[str] = None
    internal_notes: Optional[str] = None
    required_skills: List[str]
    optional_skills: Optional[List[str]] = None
    min_years_experience: Optional[int] = 0
    preferred_certifications: Optional[List[str]] = None
    visibility: Optional[str] = "invite_only"

class JobUpdate(BaseModel):
    title: Optional[str] = None
    team: Optional[str] = None
    description: Optional[str] = None
    short_description: Optional[str] = None
    internal_notes: Optional[str] = None
    required_skills: Optional[List[str]] = None
    optional_skills: Optional[List[str]] = None
    min_years_experience: Optional[int] = None
    preferred_certifications: Optional[List[str]] = None
    status: Optional[str] = None
    visibility: Optional[str] = None

class JobResponse(BaseModel):
    id: str
    title: str
    team: str
    description: str
    short_description: Optional[str] = None
    internal_notes: Optional[str] = None
    required_skills: List[str] = []
    optional_skills: List[str] = []
    min_years_experience: int = 0
    preferred_certifications: List[str] = []
    status: str
    visibility: str = "invite_only"
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
    skills_match: List[str]
    
    class Config:
        from_attributes = True

class EmployeeJobMatchResponse(BaseModel):
    job: JobResponse
    score: int
    
    class Config:
        from_attributes = True
