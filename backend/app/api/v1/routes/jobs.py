from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload
from uuid import UUID
import logging
from app.db.session import get_db
from app.models.employee import Employee
from app.models.job import Job, JobMatch
from app.schemas.job import JobCreate, JobUpdate, JobResponse, JobMatchResponse
from app.schemas.employee import EmployeeResponse
from app.api.v1.deps import get_current_user, require_manager_or_hr_or_admin, require_hr_or_admin, require_authenticated
from app.services.job_service import JobService
from app.services.match_service import MatchService

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=List[JobResponse])
async def get_jobs(
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(require_authenticated())
):
    """Get all jobs (filtered by role if needed)"""
    query = select(Job).options(selectinload(Job.manager))
    
    # If employee, only show open jobs
    if current_user.role == "employee":
        query = query.where(Job.status == "open")
    
    result = await db.execute(query)
    jobs = result.scalars().all()
    
    return [
        JobResponse(
            id=str(job.id),
            title=job.title,
            team=job.team,
            description=job.description,
            short_description=getattr(job, 'short_description', None),
            internal_notes=getattr(job, 'internal_notes', None),
            required_skills=job.required_skills or [],
            optional_skills=getattr(job, 'optional_skills', None) or [],
            min_years_experience=getattr(job, 'min_years_experience', None) or 0,
            preferred_certifications=getattr(job, 'preferred_certifications', None) or [],
            status=job.status,
            visibility=getattr(job, 'visibility', 'invite_only'),
            manager_id=str(job.manager_id),
            manager_name=job.manager.name,
            created_at=job.created_at
        )
        for job in jobs
    ]

@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Get job by ID"""
    result = await db.execute(
        select(Job).options(selectinload(Job.manager)).where(Job.id == job_id)
    )
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    return JobResponse(
        id=str(job.id),
        title=job.title,
        team=job.team,
        description=job.description,
        short_description=getattr(job, 'short_description', None),
        internal_notes=getattr(job, 'internal_notes', None),
        required_skills=job.required_skills or [],
        optional_skills=getattr(job, 'optional_skills', []),
        min_years_experience=getattr(job, 'min_years_experience', 0),
        preferred_certifications=getattr(job, 'preferred_certifications', []),
        status=job.status,
        visibility=getattr(job, 'visibility', 'invite_only'),
        manager_id=str(job.manager_id),
        manager_name=job.manager.name,
        created_at=job.created_at
    )

@router.post("/", response_model=JobResponse)
async def create_job(
    job_data: JobCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(require_manager_or_hr_or_admin())
):
    """Create a new job"""
    job_service = JobService(db)
    job = await job_service.create_job(job_data, current_user.id)
    
    return JobResponse(
        id=str(job.id),
        title=job.title,
        team=job.team,
        description=job.description,
        short_description=getattr(job, 'short_description', None),
        internal_notes=getattr(job, 'internal_notes', None),
        required_skills=job.required_skills or [],
        optional_skills=getattr(job, 'optional_skills', []),
        min_years_experience=getattr(job, 'min_years_experience', 0),
        preferred_certifications=getattr(job, 'preferred_certifications', []),
        status=job.status,
        visibility=getattr(job, 'visibility', 'invite_only'),
        manager_id=str(job.manager_id),
        manager_name=current_user.name,
        created_at=job.created_at
    )

@router.put("/{job_id}", response_model=JobResponse)
async def update_job(
    job_id: UUID,
    job_data: JobUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Update a job"""
    job_service = JobService(db)
    job = await job_service.update_job(job_id, job_data, current_user)
    
    return JobResponse(
        id=str(job.id),
        title=job.title,
        team=job.team,
        description=job.description,
        short_description=getattr(job, 'short_description', None),
        internal_notes=getattr(job, 'internal_notes', None),
        required_skills=job.required_skills or [],
        optional_skills=getattr(job, 'optional_skills', []),
        min_years_experience=getattr(job, 'min_years_experience', 0),
        preferred_certifications=getattr(job, 'preferred_certifications', []),
        status=job.status,
        visibility=getattr(job, 'visibility', 'invite_only'),
        manager_id=str(job.manager_id),
        manager_name=job.manager.name,
        created_at=job.created_at
    )

@router.delete("/{job_id}")
async def delete_job(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(get_current_user)
):
    """Delete a job"""
    job_service = JobService(db)
    await job_service.delete_job(job_id, current_user)
    
    return {"message": "Job deleted successfully"}

@router.post("/{job_id}/match")
async def trigger_matching(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(require_hr_or_admin())
):
    """Trigger AI matching for a job (HR only)"""
    logger.info(f"HR user {current_user.employee_id} triggering matching for job_id: {job_id}")
    
    try:
        match_service = MatchService(db)
        await match_service.trigger_job_matching(str(job_id))
        
        logger.info(f"Matching triggered successfully for job_id: {job_id}")
        return {"message": "Matching triggered successfully"}
        
    except Exception as e:
        logger.error(f"Error triggering matching for job {job_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error triggering matching: {str(e)}")

@router.get("/{job_id}/matches", response_model=List[JobMatchResponse])
async def get_job_matches(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(require_hr_or_admin())
):
    """Get matches for a job (HR only)"""
    logger.info(f"HR user {current_user.employee_id} viewing matches for job_id: {job_id}")
    
    result = await db.execute(
        select(JobMatch)
        .options(selectinload(JobMatch.employee))
        .where(JobMatch.job_id == job_id)
        .order_by(JobMatch.score.desc())
    )
    matches = result.scalars().all()
    
    return [
        JobMatchResponse(
            employee_id=str(match.employee_id),
            employee_name=match.employee.name,
            employee_email=match.employee.email,
            score=match.score,
            skills_match=match.employee.technical_skills
        )
        for match in matches
    ]

@router.get("/{job_id}/discover", response_model=List[EmployeeResponse])
async def discover_candidates(
    job_id: UUID,
    skills: str = Query(None, description="Comma-separated list of skills to filter by"),
    min_score: float = Query(50.0, description="Minimum match score (0-100)"),
    exclude_shortlisted: bool = Query(True, description="Exclude already shortlisted candidates"),
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(require_manager_or_hr_or_admin())
):
    """Discover potential candidates for a job (Manager/HR only)"""
    logger.info(f"User {current_user.employee_id} discovering candidates for job {job_id}")
    
    # Verify job exists and user has permission
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check permissions - only job owner or HR/admin can discover
    if current_user.role not in ["hr", "admin"] and job.manager_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to discover candidates for this job"
        )
    
    # Build query for discovering candidates
    query = select(Employee).where(
        and_(
            Employee.visibility_opt_out == False,
            Employee.id != current_user.id  # Don't include current user
        )
    )
    
    # Filter by skills if provided
    if skills:
        skill_list = [skill.strip().lower() for skill in skills.split(",")]
        skill_conditions = []
        for skill in skill_list:
            skill_conditions.append(Employee.technical_skills.contains(skill))
        query = query.where(or_(*skill_conditions))
    
    # Execute query
    result = await db.execute(query)
    candidates = result.scalars().all()
    
    # If exclude_shortlisted, remove those already shortlisted
    if exclude_shortlisted:
        shortlisted_result = await db.execute(
            select(JobMatch.employee_id).where(
                and_(
                    JobMatch.job_id == job_id,
                    JobMatch.shortlisted == True
                )
            )
        )
        shortlisted_ids = {row[0] for row in shortlisted_result}
        candidates = [c for c in candidates if c.id not in shortlisted_ids]
    
    # Calculate match scores if match service available
    try:
        match_service = MatchService()
        scored_candidates = []
        
        for candidate in candidates:
            score = await match_service.calculate_match_score(job, candidate, db)
            if score >= min_score:
                scored_candidates.append((candidate, score))
        
        # Sort by score descending
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        candidates = [candidate for candidate, score in scored_candidates]
        
    except Exception as e:
        logger.warning(f"Match scoring failed: {e}, returning unscored results")
    
    return [
        EmployeeResponse(
            id=str(candidate.id),
            employee_id=candidate.employee_id,
            name=candidate.name,
            email=candidate.email,
            role=candidate.role,
            technical_skills=candidate.technical_skills or [],
            years_experience=candidate.years_experience or 0,
            current_job_title=getattr(candidate, 'current_job_title', None),
            preferred_roles=getattr(candidate, 'preferred_roles', None) or [],
            certifications=candidate.certifications or []
        )
        for candidate in candidates
    ]

@router.post("/{job_id}/shortlist/{employee_id}")
async def shortlist_candidate(
    job_id: UUID,
    employee_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(require_manager_or_hr_or_admin())
):
    """Add candidate to shortlist for a job (Manager/HR only)"""
    logger.info(f"User {current_user.employee_id} shortlisting employee {employee_id} for job {job_id}")
    
    # Verify job exists and user has permission
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check permissions
    if current_user.role not in ["hr", "admin"] and job.manager_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to shortlist candidates for this job"
        )
    
    # Verify employee exists
    emp_result = await db.execute(select(Employee).where(Employee.id == employee_id))
    employee = emp_result.scalar_one_or_none()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    # Check if match already exists
    existing_result = await db.execute(
        select(JobMatch).where(
            and_(
                JobMatch.job_id == job_id,
                JobMatch.employee_id == employee_id
            )
        )
    )
    existing_match = existing_result.scalar_one_or_none()
    
    if existing_match:
        # Update existing match
        existing_match.shortlisted = True
        logger.info(f"Updated existing match to shortlisted for employee {employee_id}")
    else:
        # Create new match record
        try:
            match_service = MatchService()
            score = await match_service.calculate_match_score(job, employee, db)
        except Exception as e:
            logger.warning(f"Match scoring failed: {e}, using default score")
            score = 50.0
        
        job_match = JobMatch(
            job_id=job_id,
            employee_id=employee_id,
            score=score,
            shortlisted=True,
            explanation=f"Shortlisted by {current_user.name}"
        )
        db.add(job_match)
        logger.info(f"Created new shortlisted match for employee {employee_id}")
    
    await db.commit()
    
    return {"message": "Candidate successfully shortlisted"}

@router.get("/{job_id}/shortlist", response_model=List[EmployeeResponse])
async def get_shortlisted_candidates(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(require_manager_or_hr_or_admin())
):
    """Get shortlisted candidates for a job (Manager/HR only)"""
    logger.info(f"User {current_user.employee_id} getting shortlisted candidates for job {job_id}")
    
    # Verify job exists and user has permission
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check permissions
    if current_user.role not in ["hr", "admin"] and job.manager_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view shortlisted candidates for this job"
        )
    
    # Get shortlisted candidates
    result = await db.execute(
        select(Employee)
        .join(JobMatch)
        .where(
            and_(
                JobMatch.job_id == job_id,
                JobMatch.shortlisted == True
            )
        )
        .order_by(JobMatch.score.desc())
    )
    candidates = result.scalars().all()
    
    return [
        EmployeeResponse(
            id=str(candidate.id),
            employee_id=candidate.employee_id,
            name=candidate.name,
            email=candidate.email,
            role=candidate.role,
            technical_skills=candidate.technical_skills or [],
            years_experience=candidate.years_experience or 0,
            current_job_title=getattr(candidate, 'current_job_title', None),
            preferred_roles=getattr(candidate, 'preferred_roles', None) or [],
            certifications=candidate.certifications or []
        )
        for candidate in candidates
    ]
