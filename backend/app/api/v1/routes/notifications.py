from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.notification import Notification
from app.schemas.notification import NotificationResponse, NotificationMarkRead
from app.api.v1.deps import get_current_user, require_authenticated
from app.models.employee import Employee
from app.services.notification_service import NotificationService

router = APIRouter()

@router.get("/", response_model=List[NotificationResponse])
async def get_notifications(
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(require_authenticated())
):
    """Get all notifications for the current user"""
    try:
        notification_service = NotificationService(db)
        notifications = await notification_service.get_user_notifications(current_user.id)
        
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

@router.get("/unread-count")
async def get_unread_count(
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(require_authenticated())
):
    """Get count of unread notifications"""
    try:
        notification_service = NotificationService(db)
        count = await notification_service.get_unread_count(current_user.id)
        return {"unread_count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting unread count: {str(e)}")

@router.post("/mark-read")
async def mark_notifications_read(
    notification_data: NotificationMarkRead,
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(require_authenticated())
):
    """Mark notifications as read"""
    try:
        notification_service = NotificationService(db)
        success = await notification_service.mark_as_read(
            notification_data.notification_ids, 
            current_user.id
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="No notifications found or unauthorized")
        
        return {"message": f"Marked {len(notification_data.notification_ids)} notifications as read"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error marking notifications as read: {str(e)}")

@router.post("/mark-all-read")
async def mark_all_notifications_read(
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(require_authenticated())
):
    """Mark all notifications as read for the current user"""
    try:
        notification_service = NotificationService(db)
        success = await notification_service.mark_all_as_read(current_user.id)
        
        return {"message": "All notifications marked as read"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error marking all notifications as read: {str(e)}")

@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(require_authenticated())
):
    """Delete a specific notification"""
    try:
        notification_service = NotificationService(db)
        success = await notification_service.delete_notification(
            notification_id, 
            current_user.id
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Notification not found or unauthorized")
        
        return {"message": "Notification deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting notification: {str(e)}")
