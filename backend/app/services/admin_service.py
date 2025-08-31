from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from sqlalchemy.orm import selectinload
from app.models.employee import Employee
from app.models.job import Job
from app.models.application import Application
from app.models.notification import Notification

class AdminService:
    """Service for admin-related operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_all_users(self) -> List[Employee]:
        """Get all users in the system"""
        stmt = select(Employee).options(selectinload(Employee.applications))
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def update_user_role(self, user_id: UUID, new_role: str) -> Optional[Employee]:
        """Update a user's role"""
        valid_roles = ["employee", "manager", "hr", "admin"]
        if new_role not in valid_roles:
            raise ValueError(f"Invalid role. Must be one of: {valid_roles}")
        
        # Get the user
        stmt = select(Employee).where(Employee.id == user_id)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            return None
        
        # Update role
        user.role = new_role
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def delete_user(self, user_id: UUID) -> bool:
        """Delete a user (soft delete by deactivating)"""
        stmt = select(Employee).where(Employee.id == user_id)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            return False
        
        # Instead of hard delete, deactivate the user
        user.is_active = False
        await self.db.commit()
        
        return True
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """Get system-wide statistics"""
        # Count users by role
        users_by_role = await self.db.execute(
            select(Employee.role, func.count(Employee.id))
            .group_by(Employee.role)
        )
        
        # Count total jobs
        total_jobs = await self.db.execute(select(func.count(Job.id)))
        
        # Count total applications
        total_applications = await self.db.execute(select(func.count(Application.id)))
        
        # Count active users
        active_users = await self.db.execute(
            select(func.count(Employee.id))
            .where(Employee.is_active == True)
        )
        
        # Count unread notifications
        unread_notifications = await self.db.execute(
            select(func.count(Notification.id))
            .where(Notification.read == False)
        )
        
        role_counts = {role: count for role, count in users_by_role.fetchall()}
        
        return {
            "users_by_role": role_counts,
            "total_jobs": total_jobs.scalar() or 0,
            "total_applications": total_applications.scalar() or 0,
            "active_users": active_users.scalar() or 0,
            "unread_notifications": unread_notifications.scalar() or 0,
            "total_users": sum(role_counts.values())
        }
    
    async def retrain_matching_model(self) -> Dict[str, Any]:
        """Trigger retraining of the semantic matching model"""
        from app.services.semantic_match_service import PureSemanticMatchService
        
        # Get all jobs for retraining
        stmt = select(Job)
        result = await self.db.execute(stmt)
        jobs = result.scalars().all()
        
        if not jobs:
            return {
                "status": "skipped",
                "message": "No jobs found for training",
                "jobs_processed": 0
            }
        
        # Initialize the semantic matching service
        semantic_service = PureSemanticMatchService()
        
        # Process each job to update semantic matches
        jobs_processed = 0
        for job in jobs:
            try:
                matches = await semantic_service.calculate_semantic_matches(job, self.db)
                jobs_processed += 1
            except Exception as e:
                print(f"Error processing job {job.id}: {e}")
                continue
        
        return {
            "status": "completed",
            "message": "Semantic matching model retrained successfully",
            "jobs_processed": jobs_processed,
            "total_jobs": len(jobs)
        }
    
    async def get_recent_activity(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent system activity"""
        # Get recent applications
        recent_apps = await self.db.execute(
            select(Application, Employee, Job)
            .join(Employee, Application.employee_id == Employee.id)
            .join(Job, Application.job_id == Job.id)
            .order_by(Application.created_at.desc())
            .limit(limit)
        )
        
        activities = []
        for app, employee, job in recent_apps.fetchall():
            activities.append({
                "type": "application",
                "timestamp": app.created_at.isoformat(),
                "description": f"{employee.name} applied for {job.title}",
                "user": employee.name,
                "job": job.title,
                "status": app.status
            })
        
        return sorted(activities, key=lambda x: x["timestamp"], reverse=True)[:limit]
    
    async def create_system_notification(
        self, 
        content: str, 
        target_roles: Optional[List[str]] = None
    ) -> int:
        """Create system-wide notifications for users with specific roles"""
        # Get target users
        if target_roles:
            stmt = select(Employee).where(Employee.role.in_(target_roles))
        else:
            stmt = select(Employee)
            
        result = await self.db.execute(stmt)
        users = result.scalars().all()
        
        # Create notifications
        notifications_created = 0
        for user in users:
            notification = Notification(
                user_id=user.id,
                content=content,
                type="system",
                read=False
            )
            self.db.add(notification)
            notifications_created += 1
        
        await self.db.commit()
        return notifications_created