from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from app.models.notification import Notification
from app.models.employee import Employee
from app.schemas.notification import NotificationCreate, NotificationResponse

class NotificationService:
    """Service for managing notifications"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_notification(
        self, 
        user_id: UUID, 
        content: str, 
        notification_type: str = "info"
    ) -> Notification:
        """Create a new notification for a user"""
        notification = Notification(
            user_id=user_id,
            content=content,
            read=False
        )
        
        self.db.add(notification)
        await self.db.commit()
        await self.db.refresh(notification)
        return notification
    
    async def get_user_notifications(
        self, 
        user_id: UUID, 
        unread_only: bool = False
    ) -> List[Notification]:
        """Get all notifications for a user"""
        query = select(Notification).where(Notification.user_id == user_id)
        
        if unread_only:
            query = query.where(Notification.read == False)
            
        query = query.order_by(Notification.created_at.desc())
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def mark_as_read(self, notification_ids: List[UUID], user_id: UUID) -> bool:
        """Mark specific notifications as read"""
        stmt = update(Notification).where(
            Notification.id.in_(notification_ids),
            Notification.user_id == user_id
        ).values(read=True)
        
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0
    
    async def mark_all_as_read(self, user_id: UUID) -> bool:
        """Mark all notifications as read for a user"""
        stmt = update(Notification).where(
            Notification.user_id == user_id,
            Notification.read == False
        ).values(read=True)
        
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0
    
    async def delete_notification(self, notification_id: UUID, user_id: UUID) -> bool:
        """Delete a specific notification"""
        stmt = delete(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == user_id
        )
        
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0
    
    async def get_unread_count(self, user_id: UUID) -> int:
        """Get count of unread notifications for a user"""
        stmt = select(Notification).where(
            Notification.user_id == user_id,
            Notification.read == False
        )
        
        result = await self.db.execute(stmt)
        notifications = result.scalars().all()
        return len(notifications)
    
    async def create_bulk_notifications(
        self, 
        user_ids: List[UUID], 
        content: str, 
        notification_type: str = "info"
    ) -> List[Notification]:
        """Create notifications for multiple users"""
        notifications = []
        
        for user_id in user_ids:
            notification = Notification(
                user_id=user_id,
                content=content,
                read=False
            )
            notifications.append(notification)
            self.db.add(notification)
        
        await self.db.commit()
        
        # Refresh all notifications
        for notification in notifications:
            await self.db.refresh(notification)
            
        return notifications
    
    async def notify_job_comment(
        self, 
        job, 
        comment_author: Employee, 
        comment_content: str
    ) -> List[Notification]:
        """Send notifications when a new comment is added to a job"""
        recipients = []
        
        # If comment author is manager, notify HR users
        if comment_author.role == "manager":
            # Get all HR users
            hr_result = await self.db.execute(
                select(Employee).where(Employee.role == "hr")
            )
            hr_users = hr_result.scalars().all()
            recipients.extend([hr.id for hr in hr_users])
            
        # If comment author is HR, notify the job manager
        elif comment_author.role == "hr":
            if job.manager_id != comment_author.id:  # Don't notify self
                recipients.append(job.manager_id)
        
        # If comment author is admin, notify both manager and HR
        elif comment_author.role == "admin":
            # Notify job manager
            if job.manager_id != comment_author.id:
                recipients.append(job.manager_id)
            
            # Notify HR users
            hr_result = await self.db.execute(
                select(Employee).where(Employee.role == "hr")
            )
            hr_users = hr_result.scalars().all()
            recipients.extend([hr.id for hr in hr_users if hr.id != comment_author.id])
        
        # Remove duplicates and self
        recipients = list(set(recipients))
        if comment_author.id in recipients:
            recipients.remove(comment_author.id)
        
        if not recipients:
            return []
        
        # Create notification content
        content = f"New comment on job '{job.title}' by {comment_author.name}: {comment_content[:100]}{'...' if len(comment_content) > 100 else ''}"
        
        return await self.create_bulk_notifications(
            user_ids=recipients,
            content=content,
            notification_type="job_comment"
        )