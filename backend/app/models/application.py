from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Application(BaseModel):
    __tablename__ = "applications"
    
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    status = Column(String(50), default="applied")  # applied, manager_review, hr_review, approved, rejected
    manager_comment = Column(Text)
    hr_comment = Column(Text)
    
    # Relationships
    job = relationship("Job", back_populates="applications")
    employee = relationship("Employee", back_populates="applications")
    approvals = relationship("Approval", back_populates="application")