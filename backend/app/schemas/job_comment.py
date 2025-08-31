from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class JobCommentCreate(BaseModel):
    content: str

class JobCommentResponse(BaseModel):
    id: str
    job_id: str
    author_id: str
    author_name: str
    author_role: str
    content: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class JobCommentUpdate(BaseModel):
    content: str
