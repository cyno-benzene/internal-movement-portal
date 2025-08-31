from sqlalchemy import Column, String, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import BaseModel

class JobComment(BaseModel):
    __tablename__ = "job_comments"
    
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False)
    author_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    content = Column(Text, nullable=False)
    
    # Relationships
    job = relationship("Job", back_populates="comments")
    author = relationship("Employee", back_populates="job_comments")
