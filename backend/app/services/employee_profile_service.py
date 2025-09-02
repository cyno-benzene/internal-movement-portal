"""
Employee Profile Service
Handles enhanced employee profile management including work experiences
"""
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, func
from sqlalchemy.orm import selectinload

from app.models.employee import Employee, WorkExperience
from app.schemas.employee import (
    EmployeeProfileUpdate, 
    WorkExperienceCreate, 
    WorkExperienceUpdate,
    WorkExperienceResponse
)


class EmployeeProfileService:
    """Service for managing enhanced employee profiles"""
    
    @staticmethod
    async def get_employee_with_work_experience(
        db: AsyncSession, 
        employee_id: str
    ) -> Optional[Employee]:
        """Get employee with all work experiences"""
        query = select(Employee).options(
            selectinload(Employee.work_experiences)
        ).where(Employee.employee_id == employee_id)
        
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def update_employee_profile(
        db: AsyncSession,
        employee_id: str,
        profile_update: EmployeeProfileUpdate
    ) -> Optional[Employee]:
        """Update employee profile with enhanced fields"""
        
        # Get the employee
        employee = await EmployeeProfileService.get_employee_with_work_experience(
            db, employee_id
        )
        if not employee:
            return None
        
        # Update fields if provided
        update_data = profile_update.model_dump(exclude_unset=True)
        
        # Handle work experiences separately
        work_experiences_data = update_data.pop('work_experiences', None)
        
        # Handle date_of_joining and calculate months in company
        if 'date_of_joining' in update_data and update_data['date_of_joining']:
            employee.date_of_joining = update_data['date_of_joining']
            # Calculate months in company
            employee.months = EmployeeProfileService.calculate_months_in_company(
                update_data['date_of_joining']
            )
        
        # Update other fields
        for field, value in update_data.items():
            if field != 'date_of_joining' and hasattr(employee, field):
                setattr(employee, field, value)
        
        # Handle work experiences if provided
        if work_experiences_data is not None:
            # Clear existing work experiences
            await db.execute(
                delete(WorkExperience).where(WorkExperience.employee_id == employee_id)
            )
            
            # Add new work experiences
            for work_exp_data in work_experiences_data:
                work_exp = WorkExperience(
                    employee_id=employee_id,
                    **work_exp_data
                )
                # Calculate duration
                work_exp.duration_months = work_exp.calculate_duration_months()
                db.add(work_exp)
        
        employee.updated_at = datetime.utcnow()
        await db.commit()
        
        # Force refresh the session to clear cached data
        await db.refresh(employee)
        
        # Reload employee with work experiences to ensure proper async loading
        updated_employee = await EmployeeProfileService.get_employee_with_work_experience(
            db, employee_id
        )
        
        return updated_employee
    
    @staticmethod
    def calculate_months_in_company(date_of_joining: date) -> int:
        """Calculate months between date_of_joining and today"""
        today = date.today()
        months = (today.year - date_of_joining.year) * 12 + (today.month - date_of_joining.month)
        return max(0, months)
    
    @staticmethod
    async def add_work_experience(
        db: AsyncSession,
        employee_id: str,
        work_exp_data: WorkExperienceCreate
    ) -> Optional[WorkExperience]:
        """Add new work experience for an employee"""
        
        # Verify employee exists
        employee = await db.get(Employee, employee_id)
        if not employee:
            return None
        
        # If this is marked as current, update other experiences to not current
        if work_exp_data.is_current:
            await db.execute(
                update(WorkExperience)
                .where(WorkExperience.employee_id == employee_id)
                .values(is_current=False)
            )
        
        # Create new work experience
        work_exp = WorkExperience(
            employee_id=employee_id,
            **work_exp_data.model_dump()
        )
        
        # Calculate duration
        work_exp.duration_months = work_exp.calculate_duration_months()
        
        db.add(work_exp)
        await db.commit()
        await db.refresh(work_exp)
        
        # Update employee's total experience
        await EmployeeProfileService.update_total_experience(db, employee_id)
        
        return work_exp
    
    @staticmethod
    async def update_work_experience(
        db: AsyncSession,
        employee_id: str,
        work_exp_id: int,
        work_exp_update: WorkExperienceUpdate
    ) -> Optional[WorkExperience]:
        """Update an existing work experience"""
        
        # Get the work experience
        query = select(WorkExperience).where(
            and_(
                WorkExperience.id == work_exp_id,
                WorkExperience.employee_id == employee_id
            )
        )
        result = await db.execute(query)
        work_exp = result.scalar_one_or_none()
        
        if not work_exp:
            return None
        
        # If setting as current, update others to not current
        update_data = work_exp_update.model_dump(exclude_unset=True)
        if update_data.get('is_current'):
            await db.execute(
                update(WorkExperience)
                .where(
                    and_(
                        WorkExperience.employee_id == employee_id,
                        WorkExperience.id != work_exp_id
                    )
                )
                .values(is_current=False)
            )
        
        # Update fields
        for field, value in update_data.items():
            setattr(work_exp, field, value)
        
        # Recalculate duration
        work_exp.duration_months = work_exp.calculate_duration_months()
        work_exp.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(work_exp)
        
        # Update employee's total experience
        await EmployeeProfileService.update_total_experience(db, employee_id)
        
        return work_exp
    
    @staticmethod
    async def delete_work_experience(
        db: AsyncSession,
        employee_id: str,
        work_exp_id: int
    ) -> bool:
        """Delete a work experience"""
        
        query = select(WorkExperience).where(
            and_(
                WorkExperience.id == work_exp_id,
                WorkExperience.employee_id == employee_id
            )
        )
        result = await db.execute(query)
        work_exp = result.scalar_one_or_none()
        
        if not work_exp:
            return False
        
        await db.delete(work_exp)
        await db.commit()
        
        # Update employee's total experience
        await EmployeeProfileService.update_total_experience(db, employee_id)
        
        return True
    
    @staticmethod
    async def get_work_experiences(
        db: AsyncSession,
        employee_id: str
    ) -> List[WorkExperience]:
        """Get all work experiences for an employee"""
        
        query = select(WorkExperience).where(
            WorkExperience.employee_id == employee_id
        ).order_by(WorkExperience.start_date.desc())
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def update_total_experience(
        db: AsyncSession,
        employee_id: str
    ) -> None:
        """Calculate and update total career experience for an employee"""
        
        # Sum all work experience durations
        query = select(func.sum(WorkExperience.duration_months)).where(
            WorkExperience.employee_id == employee_id
        )
        result = await db.execute(query)
        total_months = result.scalar() or 0
        
        # Update employee record
        await db.execute(
            update(Employee)
            .where(Employee.employee_id == employee_id)
            .values(months_experience=total_months)
        )
        await db.commit()
    
    @staticmethod
    async def get_employees_by_manager(
        db: AsyncSession,
        manager_id: str
    ) -> List[Employee]:
        """Get all employees reporting to a specific manager"""
        
        query = select(Employee).where(
            Employee.reporting_officer_id == manager_id
        ).options(selectinload(Employee.work_experiences))
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def search_employees_by_experience(
        db: AsyncSession,
        company_name: Optional[str] = None,
        job_title: Optional[str] = None,
        skills: Optional[List[str]] = None,
        min_experience_months: Optional[int] = None
    ) -> List[Employee]:
        """Search employees by work experience criteria"""
        
        # Start with base employee query
        query = select(Employee).options(selectinload(Employee.work_experiences))
        
        conditions = []
        
        # Filter by minimum experience
        if min_experience_months:
            conditions.append(Employee.months_experience >= min_experience_months)
        
        # Filter by work experience criteria
        if company_name or job_title or skills:
            work_exp_subquery = select(WorkExperience.employee_id).distinct()
            
            work_exp_conditions = []
            
            if company_name:
                work_exp_conditions.append(
                    WorkExperience.company_name.ilike(f"%{company_name}%")
                )
            
            if job_title:
                work_exp_conditions.append(
                    WorkExperience.job_title.ilike(f"%{job_title}%")
                )
            
            if skills:
                # Search in skills_used JSONB array
                for skill in skills:
                    work_exp_conditions.append(
                        WorkExperience.skills_used.op('@>')([skill])
                    )
            
            if work_exp_conditions:
                work_exp_subquery = work_exp_subquery.where(
                    and_(*work_exp_conditions)
                )
                conditions.append(
                    Employee.employee_id.in_(work_exp_subquery)
                )
        
        if conditions:
            query = query.where(and_(*conditions))
        
        result = await db.execute(query)
        return result.scalars().all()
