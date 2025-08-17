from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class InvitationCreate(BaseModel):
    job_id: str
    employee_ids: List[str]
    content: Optional[str] = None
    manager_notes: Optional[str] = None

class InvitationResponse(BaseModel):
    id: str
    job_id: str
    employee_id: str
    inviter_id: str
    channel: str
    content: Optional[str]
    status: str
    manager_notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class InvitationDetailResponse(BaseModel):
    id: str
    job: dict  # JobResponse
    employee: dict  # EmployeeProfileResponse  
    inviter: dict  # EmployeeProfileResponse
    channel: str
    content: Optional[str]
    status: str
    manager_notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class InvitationDecisionCreate(BaseModel):
    decision: str  # accept, decline, request_info
    note: Optional[str] = None

class InvitationDecisionResponse(BaseModel):
    id: str
    invitation_id: str
    actor_id: str
    decision: str
    note: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class JobDiscoveryRequest(BaseModel):
    limit: Optional[int] = 10
    min_score: Optional[int] = 50

class ShortlistRequest(BaseModel):
    employee_ids: List[str]
    note: Optional[str] = None
