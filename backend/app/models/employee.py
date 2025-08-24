from sqlalchemy import Column, String, Integer, Text, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Employee(BaseModel):
    __tablename__ = "employees"
    
    employee_id = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="employee")  # employee, manager, hr, admin
    
    # Profile fields
    technical_skills = Column(JSONB, default=list)
    achievements = Column(JSONB, default=list)
    years_experience = Column(Integer, default=0)
    past_companies = Column(JSONB, default=list)
    certifications = Column(JSONB, default=list)
    education = Column(JSONB, default=list)
    publications = Column(JSONB, default=list)
    career_aspirations = Column(Text)
    location = Column(String(255))
    current_job_title = Column(String(255))  # Current job title
    preferred_roles = Column(JSONB, default=list)  # List of desired roles
    
    # New fields for invite-only system
    visibility_opt_out = Column(Boolean, default=False)  # if true: ineligible for discovery
    parsed_resume = Column(JSONB)  # raw structured output from parser
    
    # Relationships (using string references to avoid circular imports)
    applications = relationship("Application", back_populates="employee")
    managed_jobs = relationship("Job", back_populates="manager")
    approvals = relationship("Approval", back_populates="approver")
    notifications = relationship("Notification", back_populates="user")
    matches = relationship("JobMatch", back_populates="employee")
    received_invitations = relationship("Invitation", foreign_keys="Invitation.employee_id", back_populates="employee")
    sent_invitations = relationship("Invitation", foreign_keys="Invitation.inviter_id", back_populates="inviter")