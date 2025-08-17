from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.job import Job
from app.models.employee import Employee
from app.schemas.job import JobCreate, JobUpdate

class JobService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_job(self, job_data: JobCreate, manager_id: UUID) -> Job:
        """Create a new job posting"""
        job = Job(
            title=job_data.title,
            team=job_data.team,
            description=job_data.description,
            required_skills=job_data.required_skills,
            manager_id=manager_id,
            status="open"
        )
        
        self.db.add(job)
        await self.db.commit()
        await self.db.refresh(job)
        
        # Load manager relationship
        result = await self.db.execute(
            select(Job).options(selectinload(Job.manager)).where(Job.id == job.id)
        )
        return result.scalar_one()
    
    async def get_job(self, job_id: UUID) -> Optional[Job]:
        """Get job by ID"""
        result = await self.db.execute(
            select(Job).options(selectinload(Job.manager)).where(Job.id == job_id)
        )
        return result.scalar_one_or_none()
    
    async def update_job(self, job_id: UUID, job_data: JobUpdate, current_user: Employee) -> Job:
        """Update a job posting"""
        job = await self.get_job(job_id)
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        # Check permissions
        if current_user.role not in ["admin", "hr"] and job.manager_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this job"
            )
        
        # Update fields
        if job_data.title is not None:
            job.title = job_data.title
        if job_data.team is not None:
            job.team = job_data.team
        if job_data.description is not None:
            job.description = job_data.description
        if job_data.required_skills is not None:
            job.required_skills = job_data.required_skills
        if job_data.status is not None:
            job.status = job_data.status
        
        await self.db.commit()
        await self.db.refresh(job)
        
        # Reload with manager
        result = await self.db.execute(
            select(Job).options(selectinload(Job.manager)).where(Job.id == job.id)
        )
        return result.scalar_one()
    
    async def delete_job(self, job_id: UUID, current_user: Employee):
        """Delete a job posting"""
        job = await self.get_job(job_id)
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        # Check permissions
        if current_user.role not in ["admin", "hr"] and job.manager_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this job"
            )
        
        await self.db.delete(job)
        await self.db.commit()
    
    async def get_jobs_by_manager(self, manager_id: UUID) -> List[Job]:
        """Get all jobs managed by a specific manager"""
        result = await self.db.execute(
            select(Job).options(selectinload(Job.manager)).where(Job.manager_id == manager_id)
        )
        return result.scalars().all()
    
    async def get_open_jobs(self) -> List[Job]:
        """Get all open job positions"""
        result = await self.db.execute(
            select(Job).options(selectinload(Job.manager)).where(Job.status == "open")
        )
        return result.scalars().all()
