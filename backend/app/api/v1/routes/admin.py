from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.db.session import get_db
from app.models.employee import Employee
from app.models.job import Job
from app.models.application import Application
from app.schemas.auth import UserResponse
from app.schemas.employee import RoleUpdateRequest
from app.api.v1.deps import require_admin

router = APIRouter()

@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(require_admin())
):
    result = await db.execute(select(Employee))
    users = result.scalars().all()
    
    return [
        UserResponse(
            id=str(user.id),
            employee_id=user.employee_id,
            email=user.email,
            name=user.name,
            role=user.role
        )
        for user in users
    ]

@router.put("/users/{user_id}/role", response_model=UserResponse)
async def update_user_role(
    user_id: str,
    role_data: RoleUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(require_admin())
):
    # Validate role
    valid_roles = ["employee", "manager", "hr", "admin"]
    if role_data.role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {valid_roles}"
        )
    
    # Update user role
    result = await db.execute(
        update(Employee)
        .where(Employee.id == user_id)
        .values(role=role_data.role)
        .returning(Employee)
    )
    
    updated_user = result.scalar_one_or_none()
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    await db.commit()
    
    return UserResponse(
        id=str(updated_user.id),
        employee_id=updated_user.employee_id,
        email=updated_user.email,
        name=updated_user.name,
        role=updated_user.role
    )

@router.put("/jobs/{job_id}/reassign")
async def reassign_job(
    job_id: str,
    new_manager_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(require_admin())
):
    # Verify new manager exists and has manager role
    result = await db.execute(select(Employee).where(Employee.id == new_manager_id))
    new_manager = result.scalar_one_or_none()
    
    if not new_manager:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="New manager not found"
        )
    
    if new_manager.role not in ["manager", "hr", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must have manager, hr, or admin role"
        )
    
    # Update job
    result = await db.execute(
        update(Job)
        .where(Job.id == job_id)
        .values(manager_id=new_manager_id)
    )
    
    if result.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    await db.commit()
    return {"message": "Job reassigned successfully"}

@router.post("/applications/{application_id}/override")
async def override_application_status(
    application_id: str,
    status: str,
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(require_admin())
):
    valid_statuses = ["applied", "manager_review", "hr_review", "approved", "rejected"]
    if status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {valid_statuses}"
        )
    
    result = await db.execute(
        update(Application)
        .where(Application.id == application_id)
        .values(status=status)
    )
    
    if result.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    await db.commit()
    return {"message": "Application status overridden successfully"}