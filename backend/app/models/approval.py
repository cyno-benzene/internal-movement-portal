from sqlalchemy import Column, String, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from datetime import datetime

class Approval(BaseModel):
    __tablename__ = "approvals"
    
    application_id = Column(UUID(as_uuid=True), ForeignKey("applications.id"), nullable=False)
    approver_role = Column(String(50), nullable=False)  # manager, hr, admin
    approver_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    decision = Column(String(50), nullable=False)  # approved, rejected
    notes = Column(Text)
    decided_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    application = relationship("Application", back_populates="approvals")
    approver = relationship("Employee", back_populates="approvals")