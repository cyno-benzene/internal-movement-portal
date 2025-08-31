from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import UUID
from app.db.session import get_db
from app.models.employee import Employee
from app.models.application import Application
from app.models.job import Job
from app.schemas.application import (
    ApplicationCreate, 
    ApplicationUpdate, 
    ApplicationResponse,
    ApplicationDetailResponse
)
from app.schemas.job import JobResponse
from app.schemas.employee import EmployeeProfileResponse
from app.api.v1.deps import get_current_user, require_hr_or_admin, require_authenticated

router = APIRouter()

@router.get("/", response_model=List[ApplicationDetailResponse])
async def get_applications(
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(require_authenticated())
):
    """Get applications (filtered by role and user)"""
    query = select(Application).options(
        selectinload(Application.job).selectinload(Job.manager),
        selectinload(Application.employee)
    )
    
    # Filter based on role
    if current_user.role == "employee":
        query = query.where(Application.employee_id == current_user.id)
    elif current_user.role == "manager":
        # Show applications for jobs they manage
        query = query.join(Job).where(Job.manager_id == current_user.id)
    # HR and admin see all applications
    
    result = await db.execute(query)
    applications = result.scalars().all()
    
    return [
        ApplicationDetailResponse(
            id=str(app.id),
            job=JobResponse(
                id=str(app.job.id),
                title=app.job.title,
                team=app.job.team,
                description=app.job.description,
                note=getattr(app.job, 'note', None),
                required_skills=app.job.required_skills or [],
                optional_skills=getattr(app.job, 'optional_skills', None) or [],
                min_years_experience=getattr(app.job, 'min_years_experience', None) or 0,
                preferred_certifications=getattr(app.job, 'preferred_certifications', None) or [],
                status=app.job.status,
                manager_id=str(app.job.manager_id),
                manager_name=app.job.manager.name if app.job.manager else "Unknown",
                created_at=app.job.created_at
            ),
            employee=EmployeeProfileResponse(
                id=str(app.employee.id),
                email=app.employee.email,
                name=app.employee.name,
                role=app.employee.role,
                technical_skills=app.employee.technical_skills or [],
                achievements=app.employee.achievements or [],
                years_experience=app.employee.years_experience or 0,
                past_companies=app.employee.past_companies or [],
                certifications=app.employee.certifications or [],
                education=app.employee.education or [],
                publications=app.employee.publications or [],
                career_aspirations=app.employee.career_aspirations,
                location=app.employee.location,
                current_job_title=getattr(app.employee, 'current_job_title', None),
                preferred_roles=getattr(app.employee, 'preferred_roles', None) or [],
                visibility_opt_out=getattr(app.employee, 'visibility_opt_out', False),
                parsed_resume=getattr(app.employee, 'parsed_resume', None),
                updated_at=app.employee.updated_at
            ),
            status=app.status,
            manager_comment=app.manager_comment,
            hr_comment=app.hr_comment,
            created_at=app.created_at,
            updated_at=app.updated_at
        )
        for app in applications
    ]

@router.post("/", response_model=ApplicationResponse)
async def create_application(
    application_data: ApplicationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Create a new job application"""
    # Check if job exists and is open
    result = await db.execute(select(Job).where(Job.id == application_data.job_id))
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    if job.status != "open":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job is not open for applications"
        )
    
    # Check if user already applied
    existing_app = await db.execute(
        select(Application).where(
            Application.job_id == application_data.job_id,
            Application.employee_id == current_user.id
        )
    )
    if existing_app.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already applied for this job"
        )
    
    # Create application
    application = Application(
        job_id=application_data.job_id,
        employee_id=current_user.id,
        status="applied"
    )
    
    db.add(application)
    await db.commit()
    await db.refresh(application)
    
    return ApplicationResponse(
        id=str(application.id),
        job_id=str(application.job_id),
        employee_id=str(application.employee_id),
        status=application.status,
        manager_comment=application.manager_comment,
        hr_comment=application.hr_comment,
        created_at=application.created_at,
        updated_at=application.updated_at
    )

@router.put("/{application_id}", response_model=ApplicationResponse)
async def update_application(
    application_id: UUID,
    application_data: ApplicationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Update an application (status, comments)"""
    result = await db.execute(
        select(Application)
        .options(selectinload(Application.job))
        .where(Application.id == application_id)
    )
    application = result.scalar_one_or_none()
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    # Check permissions
    can_update = False
    if current_user.role in ["hr", "admin"]:
        can_update = True
    elif current_user.role == "manager" and application.job.manager_id == current_user.id:
        can_update = True
    elif current_user.id == application.employee_id and application_data.status is None:
        # Employees can only update their own applications and not change status
        can_update = True
    
    if not can_update:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this application"
        )
    
    # Update fields
    if application_data.status is not None:
        application.status = application_data.status
    if application_data.manager_comment is not None:
        application.manager_comment = application_data.manager_comment
    if application_data.hr_comment is not None:
        application.hr_comment = application_data.hr_comment
    
    await db.commit()
    await db.refresh(application)
    
    return ApplicationResponse(
        id=str(application.id),
        job_id=str(application.job_id),
        employee_id=str(application.employee_id),
        status=application.status,
        manager_comment=application.manager_comment,
        hr_comment=application.hr_comment,
        created_at=application.created_at,
        updated_at=application.updated_at
    )

@router.get("/me/matched-jobs", response_model=List[dict])
async def get_matched_jobs(
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Get AI-matched jobs for the current employee"""
    from app.models.job import JobMatch
    
    result = await db.execute(
        select(JobMatch)
        .options(
            selectinload(JobMatch.job).selectinload(Job.manager)
        )
        .where(JobMatch.employee_id == current_user.id)
        .order_by(JobMatch.score.desc())
    )
    matches = result.scalars().all()
    
    return [
        {
            "job": {
                "id": str(match.job.id),
                "title": match.job.title,
                "team": match.job.team,
                "description": match.job.description,
                "required_skills": match.job.required_skills,
                "status": match.job.status,
                "manager_id": str(match.job.manager_id),
                "manager_name": match.job.manager.name,
                "created_at": match.job.created_at
            },
            "score": match.score
        }
        for match in matches
    ]
