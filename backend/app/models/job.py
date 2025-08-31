from sqlalchemy import Column, String, Text, Integer, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
 

class Job(BaseModel):
    __tablename__ = "jobs"
    
    title = Column(String(255), nullable=False)
    team = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    note = Column(Text)  # Private notes for HR/Manager only
    required_skills = Column(JSONB, default=list)
    optional_skills = Column(JSONB, default=list)
    min_years_experience = Column(Integer, default=0)
    preferred_certifications = Column(JSONB, default=list)
    status = Column(String(50), default="open")  # open, closed, on_hold, cancelled
    priority = Column(String(50), default="normal")  # normal, high_importance
    matching_status = Column(String(50), default="not_matched")  # not_matched, matching, matched
    manager_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    
    # Relationships
    manager = relationship("Employee", back_populates="managed_jobs")
    applications = relationship("Application", back_populates="job", cascade="all, delete-orphan")
    matches = relationship("JobMatch", back_populates="job", cascade="all, delete-orphan")
    invitations = relationship("Invitation", back_populates="job", cascade="all, delete-orphan")
    comments = relationship("JobComment", back_populates="job", cascade="all, delete-orphan")

class JobMatch(BaseModel):
    __tablename__ = "job_matches"
    
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    score = Column(Integer, default=0)
    skills_match = Column(JSONB, default=list)  # List of matching skills
    explanation = Column(JSONB)  # per-feature contributions
    method = Column(String(50), default="semantic")
    shortlisted = Column(Boolean, default=False)
    invitation_sent = Column(Boolean, default=False)  # Track if invitation was sent
    
    # Relationships
    job = relationship("Job", back_populates="matches")
    employee = relationship("Employee", back_populates="matches")