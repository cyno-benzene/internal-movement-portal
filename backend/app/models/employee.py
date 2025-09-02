from sqlalchemy import Column, String, Integer, Text, Boolean, Date, ForeignKey
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
    months_experience = Column(Integer, default=0)  # Total career experience in months
    past_companies = Column(JSONB, default=list)  # Will be deprecated in favor of work_experiences
    certifications = Column(JSONB, default=list)
    education = Column(JSONB, default=list)
    publications = Column(JSONB, default=list)
    career_aspirations = Column(Text)
    location = Column(String(255))
    current_job_title = Column(String(255))  # Current job title
    preferred_roles = Column(JSONB, default=list)  # List of desired roles
    
    # New enhanced profile fields
    date_of_joining = Column(Date)  # Employee's start date with the company
    reporting_officer_id = Column(String(50), ForeignKey("employees.employee_id"))  # Manager's employee_id
    rep_officer_name = Column(String(255))  # Manager's name (denormalized)
    months = Column(Integer, default=0)  # Time spent in company (calculated from date_of_joining)
    
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
    job_comments = relationship("JobComment", back_populates="author")
    work_experiences = relationship("WorkExperience", back_populates="employee")
    
    # Self-referential relationship for reporting structure
    reporting_officer = relationship("Employee", remote_side=[employee_id], backref="direct_reports")

    def __repr__(self):
        return f"<Employee(name='{self.name}', employee_id='{self.employee_id}')>"


class WorkExperience(BaseModel):
    """Model for employee work experience entries"""
    __tablename__ = "work_experiences"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String(50), ForeignKey("employees.employee_id"), nullable=False)
    
    # Work experience details
    company_name = Column(String(255), nullable=False)
    job_title = Column(String(255), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)  # Null for current position
    is_current = Column(Boolean, default=False)
    
    # Experience description
    description = Column(Text)
    key_achievements = Column(JSONB, default=list)
    skills_used = Column(JSONB, default=list)
    technologies_used = Column(JSONB, default=list)
    
    # Location and employment type
    location = Column(String(255))
    employment_type = Column(String(50))  # Full-time, Part-time, Contract, Internship, etc.
    
    # Calculated fields
    duration_months = Column(Integer)  # Duration in months (calculated)
    
    # Relationships
    employee = relationship("Employee", back_populates="work_experiences")
    
    def calculate_duration_months(self):
        """Calculate duration in months with proper month counting"""
        from datetime import date
        
        end = self.end_date if self.end_date else date.today()
        start = self.start_date
        
        # Calculate months difference
        months = (end.year - start.year) * 12 + (end.month - start.month)
        
        # Add partial month if end day >= start day
        if end.day >= start.day:
            months += 1
            
        return max(0, months)  # Ensure non-negative
    
    def __repr__(self):
        return f"<WorkExperience(company='{self.company_name}', title='{self.job_title}')>"