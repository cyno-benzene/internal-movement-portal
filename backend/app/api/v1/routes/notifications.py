from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models.notification import Notification
from app.schemas.notification import NotificationResponse, NotificationMarkRead
from app.api.v1.deps import get_current_user, require_authenticated
from app.models.employee import Employee

router = APIRouter()

@router.get("/", response_model=List[NotificationResponse])
async def get_notifications(
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(require_authenticated())
):
    """Get all notifications for the current user"""
    try:
        stmt = select(Notification).where(
            Notification.user_id == current_user.id
        ).order_by(Notification.created_at.desc())
        
        result = await db.execute(stmt)
        notifications = result.scalars().all()
        
        return [
            NotificationResponse(
                id=str(notification.id),
                content=notification.content,
                read=notification.read,
                created_at=notification.created_at.isoformat()
            )
            for notification in notifications
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching notifications: {str(e)}")

@router.post("/mark-read")
async def mark_notifications_read(
    notification_data: NotificationMarkRead,
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Mark notifications as read"""
    try:
        # Verify all notifications belong to current user and update them
        stmt = update(Notification).where(
            Notification.id.in_(notification_data.notification_ids),
            Notification.user_id == current_user.id
        ).values(read=True)
        
        result = await db.execute(stmt)
        await db.commit()
        
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="No notifications found or unauthorized")
        
        return {"message": f"Marked {result.rowcount} notifications as read"}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error marking notifications as read: {str(e)}")

@router.get("/unread-count")
async def get_unread_count(
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Get count of unread notifications for the current user"""
    try:
        stmt = select(Notification).where(
            Notification.user_id == current_user.id,
            Notification.read == False
        )
        
        result = await db.execute(stmt)
        notifications = result.scalars().all()
        
        return {"unread_count": len(notifications)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting unread count: {str(e)}")

@router.post("/")
async def create_notification(
    content: str,
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Create a new notification (internal use - typically called by system)"""
    try:
        notification = Notification(
            user_id=user_id,
            content=content,
            read=False
        )
        
        db.add(notification)
        await db.commit()
        await db.refresh(notification)
        
        return NotificationResponse(
            id=str(notification.id),
            content=notification.content,
            read=notification.read,
            created_at=notification.created_at.isoformat()
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating notification: {str(e)}")
