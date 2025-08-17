from sqlalchemy import Column, String, Text, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Invitation(BaseModel):
    __tablename__ = "invitations"
    
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), nullable=False)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    inviter_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)  # manager or hr
    channel = Column(String(50), default="in-app")
    content = Column(Text)  # templated text visible to invitee
    status = Column(String(50), default="pending")  # pending, accepted, declined, cancelled
    manager_notes = Column(Text)
    
    # Relationships
    job = relationship("Job", back_populates="invitations")
    employee = relationship("Employee", foreign_keys=[employee_id], back_populates="received_invitations")
    inviter = relationship("Employee", foreign_keys=[inviter_id], back_populates="sent_invitations")
    decisions = relationship("InvitationDecision", back_populates="invitation", cascade="all, delete-orphan")

class InvitationDecision(BaseModel):
    __tablename__ = "invitation_decisions"
    
    invitation_id = Column(UUID(as_uuid=True), ForeignKey("invitations.id"), nullable=False)
    actor_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    decision = Column(String(50), nullable=False)  # accept, decline, request_info
    note = Column(Text)
    
    # Relationships
    invitation = relationship("Invitation", back_populates="decisions")
    actor = relationship("Employee")
