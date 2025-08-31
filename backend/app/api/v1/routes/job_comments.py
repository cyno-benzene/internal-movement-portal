from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import UUID

from app.db.session import get_db
from app.models.employee import Employee
from app.models.job import Job
from app.models.job_comment import JobComment
from app.schemas.job_comment import JobCommentCreate, JobCommentResponse, JobCommentUpdate
from app.api.v1.deps import require_manager_or_hr_or_admin
from app.services.notification_service import NotificationService

router = APIRouter()

@router.get("/{job_id}/comments", response_model=List[JobCommentResponse])
async def get_job_comments(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(require_manager_or_hr_or_admin())
):
    """Get all comments for a job (Manager/HR/Admin only)"""
    # First check if job exists and user has access
    job_result = await db.execute(select(Job).where(Job.id == job_id))
    job = job_result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check if user can access this job (manager of the job, HR, or admin)
    if (current_user.role not in ["hr", "admin"] and 
        job.manager_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view comments for this job"
        )
    
    # Get comments with author information
    result = await db.execute(
        select(JobComment)
        .options(selectinload(JobComment.author))
        .where(JobComment.job_id == job_id)
        .order_by(JobComment.created_at)
    )
    comments = result.scalars().all()
    
    return [
        JobCommentResponse(
            id=str(comment.id),
            job_id=str(comment.job_id),
            author_id=str(comment.author_id),
            author_name=comment.author.name,
            author_role=comment.author.role,
            content=comment.content,
            created_at=comment.created_at
        )
        for comment in comments
    ]

@router.post("/{job_id}/comments", response_model=JobCommentResponse)
async def create_job_comment(
    job_id: UUID,
    comment_data: JobCommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(require_manager_or_hr_or_admin())
):
    """Create a new comment on a job (Manager/HR/Admin only)"""
    # First check if job exists and user has access
    job_result = await db.execute(select(Job).where(Job.id == job_id))
    job = job_result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check if user can comment on this job (manager of the job, HR, or admin)
    if (current_user.role not in ["hr", "admin"] and 
        job.manager_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to comment on this job"
        )
    
    # Create the comment
    comment = JobComment(
        job_id=job_id,
        author_id=current_user.id,
        content=comment_data.content
    )
    
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    
    # Load author relationship
    result = await db.execute(
        select(JobComment)
        .options(selectinload(JobComment.author))
        .where(JobComment.id == comment.id)
    )
    comment_with_author = result.scalar_one()
    
    # Send notification to relevant users
    notification_service = NotificationService(db)
    await notification_service.notify_job_comment(
        job=job,
        comment_author=current_user,
        comment_content=comment_data.content
    )
    
    return JobCommentResponse(
        id=str(comment_with_author.id),
        job_id=str(comment_with_author.job_id),
        author_id=str(comment_with_author.author_id),
        author_name=comment_with_author.author.name,
        author_role=comment_with_author.author.role,
        content=comment_with_author.content,
        created_at=comment_with_author.created_at
    )

@router.put("/{job_id}/comments/{comment_id}", response_model=JobCommentResponse)
async def update_job_comment(
    job_id: UUID,
    comment_id: UUID,
    comment_data: JobCommentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(require_manager_or_hr_or_admin())
):
    """Update a job comment (only by the author or admin)"""
    # Get the comment
    result = await db.execute(
        select(JobComment)
        .options(selectinload(JobComment.author))
        .where(JobComment.id == comment_id, JobComment.job_id == job_id)
    )
    comment = result.scalar_one_or_none()
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    # Check if user can edit this comment (author or admin)
    if (current_user.role != "admin" and 
        comment.author_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to edit this comment"
        )
    
    # Update the comment
    comment.content = comment_data.content
    await db.commit()
    await db.refresh(comment)
    
    return JobCommentResponse(
        id=str(comment.id),
        job_id=str(comment.job_id),
        author_id=str(comment.author_id),
        author_name=comment.author.name,
        author_role=comment.author.role,
        content=comment.content,
        created_at=comment.created_at
    )

@router.delete("/{job_id}/comments/{comment_id}")
async def delete_job_comment(
    job_id: UUID,
    comment_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(require_manager_or_hr_or_admin())
):
    """Delete a job comment (only by the author or admin)"""
    # Get the comment
    result = await db.execute(
        select(JobComment).where(JobComment.id == comment_id, JobComment.job_id == job_id)
    )
    comment = result.scalar_one_or_none()
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    # Check if user can delete this comment (author or admin)
    if (current_user.role != "admin" and 
        comment.author_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this comment"
        )
    
    await db.delete(comment)
    await db.commit()
    
    return {"message": "Comment deleted successfully"}
