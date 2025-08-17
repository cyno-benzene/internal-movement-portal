from sqlalchemy import Column, String, Text, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Notification(BaseModel):
    __tablename__ = "notifications"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    content = Column(Text, nullable=False)
    read = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("Employee", back_populates="notifications")