from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.schemas.job import JobResponse
from app.schemas.employee import EmployeeProfileResponse

class ApplicationCreate(BaseModel):
    job_id: str

class ApplicationUpdate(BaseModel):
    status: Optional[str] = None
    manager_comment: Optional[str] = None
    hr_comment: Optional[str] = None

class ApplicationResponse(BaseModel):
    id: str
    job_id: str
    employee_id: str
    status: str
    manager_comment: Optional[str]
    hr_comment: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ApplicationDetailResponse(BaseModel):
    id: str
    job: JobResponse
    employee: EmployeeProfileResponse
    status: str
    manager_comment: Optional[str]
    hr_comment: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True