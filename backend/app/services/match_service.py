from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.models.employee import Employee
from app.models.job import Job, JobMatch
from app.core.logging_config import get_api_logger

logger = get_api_logger()

class MatchService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def trigger_job_matching(self, job_id: str):
        """Trigger AI matching for a specific job"""
        logger.info(f"Starting job matching for job_id: {job_id}")
        try:
            await self.calculate_matches_for_job(job_id)
            logger.info(f"Job matching completed successfully for job_id: {job_id}")
        except Exception as e:
            logger.error(f"Error during job matching for job_id {job_id}: {str(e)}")
            raise
    
    async def calculate_matches_for_job(self, job_id: str) -> List[Dict[str, Any]]:
        logger.info(f"Calculating matches for job_id: {job_id}")
        
        # Get job details
        job_result = await self.db.execute(select(Job).where(Job.id == job_id))
        job = job_result.scalar_one_or_none()
        
        if not job:
            logger.warning(f"Job not found for job_id: {job_id}")
            return []
        
        logger.info(f"Found job: {job.title}, skills: {job.required_skills}")
        
        # Get all employees
        employees_result = await self.db.execute(
            select(Employee).where(Employee.role == "employee")
        )
        employees = employees_result.scalars().all()
        
        logger.info(f"Found {len(employees)} employees to match")
        
        matches = []
        for employee in employees:
            score = self._calculate_match_score(job, employee)
            if score > 0:  # Only include matches with positive scores
                matches.append({
                    "employee_id": str(employee.id),
                    "score": score,
                    "employee": employee
                })
                logger.info(f"Employee {employee.name} scored {score} for job {job.title}")
        
        # Sort by score descending
        matches.sort(key=lambda x: x["score"], reverse=True)
        
        logger.info(f"Generated {len(matches)} matches for job {job.title}")
        
        # Store matches in database
        await self._store_matches(job_id, matches)
        
        return matches
    
    def _calculate_match_score(self, job: Job, employee: Employee) -> int:
        score = 0
        
        job_skills = job.required_skills or []
        employee_skills = employee.technical_skills or []
        
        # Exact skill match: +10
        for skill in job_skills:
            if skill.lower() in [s.lower() for s in employee_skills]:
                score += 10
        
        # Related skill (simplified - contains similar words): +5
        for job_skill in job_skills:
            for emp_skill in employee_skills:
                if (job_skill.lower() != emp_skill.lower() and 
                    (job_skill.lower() in emp_skill.lower() or emp_skill.lower() in job_skill.lower())):
                    score += 5
        
        # Years experience (assuming job requires some experience): +5
        if employee.years_experience >= 2:  # Simplified requirement
            score += 5
        
        # Relevant certification: +3
        if employee.certifications:
            score += 3
        
        # Relevant education: +2
        if employee.education:
            score += 2
        
        # Career aspirations keyword match: +2
        if employee.career_aspirations:
            for skill in job_skills:
                if skill.lower() in employee.career_aspirations.lower():
                    score += 2
        
        # Achievement relevance: +2-3
        if employee.achievements:
            score += min(len(employee.achievements), 3) * 2
        
        return score
    
    async def _store_matches(self, job_id: str, matches: List[Dict[str, Any]]):
        # Delete existing matches for this job
        await self.db.execute(delete(JobMatch).where(JobMatch.job_id == job_id))
        
        # Store new matches
        for match in matches:
            job_match = JobMatch(
                job_id=job_id,
                employee_id=match["employee_id"],
                score=match["score"]
            )
            self.db.add(job_match)
        
        await self.db.commit()
    
    async def get_matches_for_job(self, job_id: str) -> List[JobMatch]:
        result = await self.db.execute(
            select(JobMatch)
            .where(JobMatch.job_id == job_id)
            .order_by(JobMatch.score.desc())
        )
        return result.scalars().all()
    
    async def get_matched_jobs_for_employee(self, employee_id: str) -> List[JobMatch]:
        result = await self.db.execute(
            select(JobMatch)
            .where(JobMatch.employee_id == employee_id)
            .order_by(JobMatch.score.desc())
        )
        return result.scalars().all()