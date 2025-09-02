from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from app.db.session import get_db
from app.models.employee import Employee, WorkExperience
from app.schemas.employee import (
    EmployeeProfileUpdate, 
    EmployeeProfileResponse,
    WorkExperienceCreate,
    WorkExperienceUpdate,
    WorkExperienceResponse
)
from app.services.employee_profile_service import EmployeeProfileService
from app.api.v1.deps import get_current_user, require_hr_or_admin, require_authenticated

router = APIRouter()

@router.get("/me", response_model=EmployeeProfileResponse)
async def get_my_profile(
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(require_authenticated())
):
    """Get current user's enhanced profile with work experiences"""
    employee = await EmployeeProfileService.get_employee_with_work_experience(
        db, current_user.employee_id
    )
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    return EmployeeProfileResponse(
        id=str(employee.id),
        employee_id=employee.employee_id,
        email=employee.email,
        name=employee.name,
        role=employee.role,
        technical_skills=employee.technical_skills or [],
        achievements=employee.achievements or [],
        months_experience=employee.months_experience or 0,
        past_companies=employee.past_companies or [],
        certifications=employee.certifications or [],
        education=employee.education or [],
        publications=employee.publications or [],
        career_aspirations=employee.career_aspirations,
        location=employee.location,
        current_job_title=employee.current_job_title,
        preferred_roles=employee.preferred_roles or [],
        visibility_opt_out=employee.visibility_opt_out or False,
        parsed_resume=employee.parsed_resume,
        date_of_joining=employee.date_of_joining,
        reporting_officer_id=employee.reporting_officer_id,
        rep_officer_name=employee.rep_officer_name,
        months=employee.months or 0,
        work_experiences=[
            WorkExperienceResponse(
                id=we.id,
                employee_id=we.employee_id,
                company_name=we.company_name,
                job_title=we.job_title,
                start_date=we.start_date,
                end_date=we.end_date,
                is_current=we.is_current,
                description=we.description,
                key_achievements=we.key_achievements or [],
                skills_used=we.skills_used or [],
                technologies_used=we.technologies_used or [],
                location=we.location,
                employment_type=we.employment_type,
                duration_months=we.duration_months,
                created_at=we.created_at,
                updated_at=we.updated_at
            ) for we in (employee.work_experiences or [])
        ],
        updated_at=employee.updated_at
    )

@router.put("/me", response_model=EmployeeProfileResponse)
async def update_my_profile(
    profile_data: EmployeeProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(require_authenticated())
):
    """Update current user's enhanced profile"""
    
    updated_employee = await EmployeeProfileService.update_employee_profile(
        db, current_user.employee_id, profile_data
    )
    
    if not updated_employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    # Force fresh reload to ensure work experiences are up to date
    fresh_employee = await EmployeeProfileService.get_employee_with_work_experience(
        db, current_user.employee_id
    )
    
    if not fresh_employee:
        fresh_employee = updated_employee
    
    return EmployeeProfileResponse(
        id=str(fresh_employee.id),
        employee_id=fresh_employee.employee_id,
        email=fresh_employee.email,
        name=fresh_employee.name,
        role=fresh_employee.role,
        technical_skills=fresh_employee.technical_skills or [],
        achievements=fresh_employee.achievements or [],
        months_experience=fresh_employee.months_experience or 0,
        past_companies=fresh_employee.past_companies or [],
        certifications=fresh_employee.certifications or [],
        education=fresh_employee.education or [],
        publications=fresh_employee.publications or [],
        career_aspirations=fresh_employee.career_aspirations,
        location=fresh_employee.location,
        current_job_title=fresh_employee.current_job_title,
        preferred_roles=fresh_employee.preferred_roles or [],
        visibility_opt_out=fresh_employee.visibility_opt_out or False,
        parsed_resume=fresh_employee.parsed_resume,
        date_of_joining=fresh_employee.date_of_joining,
        reporting_officer_id=fresh_employee.reporting_officer_id,
        rep_officer_name=fresh_employee.rep_officer_name,
        months=fresh_employee.months or 0,
        work_experiences=[
            WorkExperienceResponse(
                id=we.id,
                employee_id=we.employee_id,
                company_name=we.company_name,
                job_title=we.job_title,
                start_date=we.start_date,
                end_date=we.end_date,
                is_current=we.is_current,
                description=we.description,
                key_achievements=we.key_achievements or [],
                skills_used=we.skills_used or [],
                technologies_used=we.technologies_used or [],
                location=we.location,
                employment_type=we.employment_type,
                duration_months=we.duration_months,
                created_at=we.created_at,
                updated_at=we.updated_at
            ) for we in (fresh_employee.work_experiences or [])
        ],
        updated_at=fresh_employee.updated_at
    )

# Work Experience Management Routes

@router.post("/me/work-experiences", response_model=WorkExperienceResponse)
async def add_work_experience(
    work_exp_data: WorkExperienceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(require_authenticated())
):
    """Add new work experience to current user's profile"""
    
    work_exp = await EmployeeProfileService.add_work_experience(
        db, current_user.employee_id, work_exp_data
    )
    
    if not work_exp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not add work experience"
        )
    
    return WorkExperienceResponse(
        id=work_exp.id,
        employee_id=work_exp.employee_id,
        company_name=work_exp.company_name,
        job_title=work_exp.job_title,
        start_date=work_exp.start_date,
        end_date=work_exp.end_date,
        is_current=work_exp.is_current,
        description=work_exp.description,
        key_achievements=work_exp.key_achievements or [],
        skills_used=work_exp.skills_used or [],
        technologies_used=work_exp.technologies_used or [],
        location=work_exp.location,
        employment_type=work_exp.employment_type,
        duration_months=work_exp.duration_months,
        created_at=work_exp.created_at,
        updated_at=work_exp.updated_at
    )

@router.delete("/me/work-experiences/{work_exp_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_work_experience(
    work_exp_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(require_authenticated())
):
    """Delete a work experience entry"""
    
    success = await EmployeeProfileService.delete_work_experience(
        db, current_user.employee_id, work_exp_id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Work experience not found"
        )

# Admin/HR Routes

@router.get("/{user_id}", response_model=EmployeeProfileResponse)
async def get_profile(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(require_hr_or_admin())
):
    """Get any user's enhanced profile (HR/Admin only)"""
    
    result = await db.execute(select(Employee).where(Employee.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get full profile with work experiences
    employee = await EmployeeProfileService.get_employee_with_work_experience(
        db, user.employee_id
    )
    
    return EmployeeProfileResponse(
        id=str(employee.id),
        employee_id=employee.employee_id,
        email=employee.email,
        name=employee.name,
        role=employee.role,
        technical_skills=employee.technical_skills or [],
        achievements=employee.achievements or [],
        months_experience=employee.months_experience or 0,
        past_companies=employee.past_companies or [],
        certifications=employee.certifications or [],
        education=employee.education or [],
        publications=employee.publications or [],
        career_aspirations=employee.career_aspirations,
        location=employee.location,
        current_job_title=employee.current_job_title,
        preferred_roles=employee.preferred_roles or [],
        visibility_opt_out=employee.visibility_opt_out or False,
        parsed_resume=employee.parsed_resume,
        date_of_joining=employee.date_of_joining,
        reporting_officer_id=employee.reporting_officer_id,
        rep_officer_name=employee.rep_officer_name,
        months=employee.months or 0,
        work_experiences=[
            WorkExperienceResponse(
                id=we.id,
                employee_id=we.employee_id,
                company_name=we.company_name,
                job_title=we.job_title,
                start_date=we.start_date,
                end_date=we.end_date,
                is_current=we.is_current,
                description=we.description,
                key_achievements=we.key_achievements or [],
                skills_used=we.skills_used or [],
                technologies_used=we.technologies_used or [],
                location=we.location,
                employment_type=we.employment_type,
                duration_months=we.duration_months,
                created_at=we.created_at,
                updated_at=we.updated_at
            ) for we in (employee.work_experiences or [])
        ],
        updated_at=employee.updated_at
    )
