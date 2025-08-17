from typing import List
from pydantic import BaseModel
from datetime import datetime

class NotificationBase(BaseModel):
    content: str

class NotificationCreate(NotificationBase):
    user_id: str

class NotificationResponse(NotificationBase):
    id: str
    read: bool
    created_at: str
    
    class Config:
        from_attributes = True

class NotificationMarkRead(BaseModel):
    notification_ids: List[str]

class NotificationUnreadCount(BaseModel):
    unread_count: int
