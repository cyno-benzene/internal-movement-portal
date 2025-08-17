from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from app.db.session import get_db
from app.models.employee import Employee
from app.schemas.employee import EmployeeProfileUpdate, EmployeeProfileResponse
from app.api.v1.deps import get_current_user, require_hr_or_admin, require_authenticated

router = APIRouter()

@router.get("/me", response_model=EmployeeProfileResponse)
async def get_my_profile(
    current_user: Employee = Depends(require_authenticated())
):
    """Get current user's profile"""
    return EmployeeProfileResponse(
        id=str(current_user.id),
        employee_id=current_user.employee_id,
        email=current_user.email,
        name=current_user.name,
        role=current_user.role,
        technical_skills=current_user.technical_skills or [],
        achievements=current_user.achievements or [],
        years_experience=current_user.years_experience or 0,
        past_companies=current_user.past_companies or [],
        certifications=current_user.certifications or [],
        education=current_user.education or [],
        publications=current_user.publications or [],
        career_aspirations=current_user.career_aspirations,
        location=current_user.location,
        current_job_title=getattr(current_user, 'current_job_title', None),
        preferred_roles=getattr(current_user, 'preferred_roles', None) or [],
        visibility_opt_out=getattr(current_user, 'visibility_opt_out', False),
        parsed_resume=getattr(current_user, 'parsed_resume', None),
        updated_at=current_user.updated_at
    )

@router.put("/me", response_model=EmployeeProfileResponse)
async def update_my_profile(
    profile_data: EmployeeProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(require_authenticated())
):
    """Update current user's profile"""
    # Update fields
    if profile_data.name is not None:
        current_user.name = profile_data.name
    if profile_data.technical_skills is not None:
        current_user.technical_skills = profile_data.technical_skills
    if profile_data.achievements is not None:
        current_user.achievements = profile_data.achievements
    if profile_data.years_experience is not None:
        current_user.years_experience = profile_data.years_experience
    if profile_data.past_companies is not None:
        current_user.past_companies = profile_data.past_companies
    if profile_data.certifications is not None:
        current_user.certifications = profile_data.certifications
    if profile_data.education is not None:
        current_user.education = profile_data.education
    if profile_data.publications is not None:
        current_user.publications = profile_data.publications
    if profile_data.career_aspirations is not None:
        current_user.career_aspirations = profile_data.career_aspirations
    if profile_data.location is not None:
        current_user.location = profile_data.location
    
    await db.commit()
    await db.refresh(current_user)
    
    return EmployeeProfileResponse(
        id=str(current_user.id),
        employee_id=current_user.employee_id,
        email=current_user.email,
        name=current_user.name,
        role=current_user.role,
        technical_skills=current_user.technical_skills or [],
        achievements=current_user.achievements or [],
        years_experience=current_user.years_experience or 0,
        past_companies=current_user.past_companies or [],
        certifications=current_user.certifications or [],
        education=current_user.education or [],
        publications=current_user.publications or [],
        career_aspirations=current_user.career_aspirations,
        location=current_user.location,
        current_job_title=getattr(current_user, 'current_job_title', None),
        preferred_roles=getattr(current_user, 'preferred_roles', None) or [],
        visibility_opt_out=getattr(current_user, 'visibility_opt_out', False),
        parsed_resume=getattr(current_user, 'parsed_resume', None),
        updated_at=current_user.updated_at
    )

@router.get("/{user_id}", response_model=EmployeeProfileResponse)
async def get_profile(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Employee = Depends(require_hr_or_admin())
):
    """Get any user's profile (HR/Admin only)"""
    result = await db.execute(select(Employee).where(Employee.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return EmployeeProfileResponse(
        id=str(user.id),
        employee_id=user.employee_id,
        email=user.email,
        name=user.name,
        role=user.role,
        technical_skills=user.technical_skills or [],
        achievements=user.achievements or [],
        years_experience=user.years_experience or 0,
        past_companies=user.past_companies or [],
        certifications=user.certifications or [],
        education=user.education or [],
        publications=user.publications or [],
        career_aspirations=user.career_aspirations,
        location=user.location,
        current_job_title=getattr(user, 'current_job_title', None),
        preferred_roles=getattr(user, 'preferred_roles', None) or [],
        visibility_opt_out=getattr(user, 'visibility_opt_out', False),
        parsed_resume=getattr(user, 'parsed_resume', None),
        updated_at=user.updated_at
    )
