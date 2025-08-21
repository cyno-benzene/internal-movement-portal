from typing import List, Dict, Any, Set
import math
from collections import defaultdict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.models.employee import Employee
from app.models.job import Job, JobMatch
from app.core.logging_config import get_api_logger

logger = get_api_logger()

class MatchService:
    def __init__(self, db: AsyncSession):
        self.db = db
        
        # Industry-standard skill weights
        self.weights = {
            'required_skills_exact': 30.0,      # Critical - exact match on required skills
            'required_skills_similar': 15.0,     # Important - similar skills to required
            'optional_skills_match': 10.0,       # Nice to have - optional skills match
            'experience_match': 20.0,            # Important - experience level match
            'career_alignment': 15.0,            # Important - career goals alignment
            'education_relevance': 5.0,          # Moderate - relevant education
            'certification_bonus': 5.0,          # Moderate - relevant certifications
        }
        
        # Skill similarity mappings (expandable)
        self.skill_synonyms = {
            'javascript': ['js', 'node.js', 'nodejs', 'react', 'vue', 'angular'],
            'python': ['django', 'flask', 'fastapi', 'pytorch', 'tensorflow'],
            'java': ['spring', 'spring boot', 'hibernate', 'maven', 'gradle'],
            'aws': ['amazon web services', 'ec2', 's3', 'lambda', 'cloud'],
            'kubernetes': ['k8s', 'docker', 'containerization', 'orchestration'],
            'sql': ['database', 'postgresql', 'mysql', 'mongodb', 'nosql'],
            'devops': ['ci/cd', 'jenkins', 'deployment', 'automation'],
            'machine learning': ['ml', 'ai', 'data science', 'analytics'],
            'react': ['reactjs', 'frontend', 'ui', 'javascript'],
            'angular': ['typescript', 'frontend', 'spa'],
        }
    
    async def trigger_job_matching(self, job_id: str):
        """Trigger AI matching for a specific job"""
        logger.info(f"Starting industry-standard job matching for job_id: {job_id}")
        try:
            await self.calculate_matches_for_job(job_id)
            logger.info(f"Job matching completed successfully for job_id: {job_id}")
        except Exception as e:
            logger.error(f"Error during job matching for job_id {job_id}: {str(e)}")
            raise
    
    async def calculate_matches_for_job(self, job_id: str) -> List[Dict[str, Any]]:
        logger.info(f"Calculating industry-standard matches for job_id: {job_id}")
        
        # Get job details
        job_result = await self.db.execute(select(Job).where(Job.id == job_id))
        job = job_result.scalar_one_or_none()
        
        if not job:
            logger.warning(f"Job not found for job_id: {job_id}")
            return []
        
        logger.info(f"Found job: {job.title}, required skills: {job.required_skills}")
        
        # Get all active employees (excluding those who opted out)
        employees_result = await self.db.execute(
            select(Employee).where(
                Employee.role == "employee"
            ).where(
                Employee.visibility_opt_out.is_(False)
            )
        )
        employees = employees_result.scalars().all()
        
        logger.info(f"Found {len(employees)} eligible employees to match")
        
        matches = []
        for employee in employees:
            score = self._calculate_industry_standard_score(job, employee)
            
            # Only include candidates with meaningful scores (>= 20%)
            if score >= 20.0:
                skills_match = self._get_matching_skills(job, employee)
                matches.append({
                    "employee_id": str(employee.id),
                    "score": round(score, 1),
                    "skills_match": skills_match,
                    "employee": employee
                })
                logger.info(f"Employee {employee.name} scored {score:.1f}% for job {job.title}")
        
        # Sort by score descending
        matches.sort(key=lambda x: x["score"], reverse=True)
        
        logger.info(f"Generated {len(matches)} qualified matches for job {job.title}")
        
        # Store matches in database
        await self._store_matches(job_id, matches)
        
        return matches
    
    def _calculate_industry_standard_score(self, job: Job, employee: Employee) -> float:
        """
        Calculate match score using industry-standard weighted approach
        Score ranges from 0-100%
        """
        total_score = 0.0
        
        job_required_skills = self._normalize_skills(job.required_skills or [])
        job_optional_skills = self._normalize_skills(getattr(job, 'optional_skills', None) or [])
        employee_skills = self._normalize_skills(employee.technical_skills or [])
        
        # 1. Required Skills Match (30% weight) - CRITICAL
        required_score = self._calculate_skills_match(job_required_skills, employee_skills)
        total_score += required_score * self.weights['required_skills_exact']
        
        # 2. Similar Skills Match (15% weight) - Semantic similarity
        similar_score = self._calculate_similar_skills_match(job_required_skills, employee_skills)
        total_score += similar_score * self.weights['required_skills_similar']
        
        # 3. Optional Skills Match (10% weight) - Nice to have
        optional_score = self._calculate_skills_match(job_optional_skills, employee_skills)
        total_score += optional_score * self.weights['optional_skills_match']
        
        # 4. Experience Match (20% weight) - Very important
        experience_score = self._calculate_experience_match(job, employee)
        total_score += experience_score * self.weights['experience_match']
        
        # 5. Career Alignment (15% weight) - Strategic fit
        career_score = self._calculate_career_alignment(job, employee)
        total_score += career_score * self.weights['career_alignment']
        
        # 6. Education Relevance (5% weight)
        education_score = self._calculate_education_relevance(job, employee)
        total_score += education_score * self.weights['education_relevance']
        
        # 7. Certification Bonus (5% weight)
        cert_score = self._calculate_certification_match(job, employee)
        total_score += cert_score * self.weights['certification_bonus']
        
        return min(total_score, 100.0)  # Cap at 100%
    
    def _normalize_skills(self, skills: List[str]) -> Set[str]:
        """Normalize skills to lowercase for comparison"""
        if not skills:
            return set()
        return {skill.lower().strip() for skill in skills if skill.strip()}
    
    def _calculate_skills_match(self, job_skills: Set[str], employee_skills: Set[str]) -> float:
        """Calculate exact skills match percentage"""
        if not job_skills:
            return 1.0  # If no skills required, full score
        
        matched_skills = job_skills.intersection(employee_skills)
        return len(matched_skills) / len(job_skills)
    
    def _calculate_similar_skills_match(self, job_skills: Set[str], employee_skills: Set[str]) -> float:
        """Calculate semantic similarity score for skills"""
        if not job_skills:
            return 0.0
        
        similarity_score = 0.0
        for job_skill in job_skills:
            if job_skill in employee_skills:
                continue  # Already counted in exact match
            
            # Check for semantic similarity
            max_similarity = 0.0
            for emp_skill in employee_skills:
                similarity = self._calculate_skill_similarity(job_skill, emp_skill)
                max_similarity = max(max_similarity, similarity)
            
            similarity_score += max_similarity
        
        return similarity_score / len(job_skills)
    
    def _calculate_skill_similarity(self, skill1: str, skill2: str) -> float:
        """Calculate similarity between two skills using synonym mapping and string similarity"""
        skill1, skill2 = skill1.lower(), skill2.lower()
        
        # Check synonym mappings
        for base_skill, synonyms in self.skill_synonyms.items():
            if skill1 == base_skill or skill1 in synonyms:
                if skill2 == base_skill or skill2 in synonyms:
                    return 0.8  # High similarity for synonyms
        
        # String containment similarity
        if skill1 in skill2 or skill2 in skill1:
            return 0.6
        
        # Jaccard similarity for word overlap
        words1 = set(skill1.split())
        words2 = set(skill2.split())
        
        if words1 and words2:
            intersection = words1.intersection(words2)
            union = words1.union(words2)
            jaccard = len(intersection) / len(union)
            return jaccard * 0.4  # Lower weight for word similarity
        
        return 0.0
    
    def _calculate_experience_match(self, job: Job, employee: Employee) -> float:
        """Calculate experience level match"""
        min_required = getattr(job, 'min_years_experience', None) or 0
        employee_exp = employee.years_experience or 0
        
        if min_required == 0:
            return 1.0  # No experience requirement
        
        if employee_exp >= min_required:
            # Bonus for more experience, but with diminishing returns
            excess_exp = employee_exp - min_required
            bonus = min(excess_exp * 0.1, 0.3)  # Max 30% bonus
            return min(1.0 + bonus, 1.0)
        else:
            # Penalty for insufficient experience
            deficit = min_required - employee_exp
            penalty = deficit * 0.2  # 20% penalty per missing year
            return max(0.0, 1.0 - penalty)
    
    def _calculate_career_alignment(self, job: Job, employee: Employee) -> float:
        """Calculate how well the job aligns with career aspirations"""
        if not employee.career_aspirations:
            return 0.5  # Neutral score if no aspirations listed
        
        aspirations = employee.career_aspirations.lower()
        job_title = job.title.lower()
        job_skills = self._normalize_skills(job.required_skills or [])
        
        score = 0.0
        
        # Check if job title appears in aspirations
        job_words = set(job_title.split())
        aspiration_words = set(aspirations.split())
        
        title_overlap = len(job_words.intersection(aspiration_words))
        if title_overlap > 0:
            score += 0.6
        
        # Check if job skills align with aspirations
        skill_mentions = 0
        for skill in job_skills:
            if skill in aspirations:
                skill_mentions += 1
        
        if job_skills:
            skill_alignment = skill_mentions / len(job_skills)
            score += skill_alignment * 0.4
        
        return min(score, 1.0)
    
    def _calculate_education_relevance(self, job: Job, employee: Employee) -> float:
        """Calculate education relevance score"""
        if not employee.education:
            return 0.0
        
        education_text = " ".join(employee.education).lower()
        job_skills = self._normalize_skills(job.required_skills or [])
        
        # Simple keyword matching for technical education
        tech_keywords = ['computer', 'software', 'engineering', 'science', 'technology', 'data']
        relevance_score = 0.0
        
        for keyword in tech_keywords:
            if keyword in education_text:
                relevance_score += 0.2
        
        # Check for skill-related education
        for skill in job_skills:
            if skill in education_text:
                relevance_score += 0.1
        
        return min(relevance_score, 1.0)
    
    def _calculate_certification_match(self, job: Job, employee: Employee) -> float:
        """Calculate certification relevance score"""
        if not employee.certifications:
            return 0.0
        
        job_preferred_certs = getattr(job, 'preferred_certifications', None) or []
        if not job_preferred_certs:
            return 0.3  # Base score for having any certifications
        
        employee_certs_text = " ".join(employee.certifications).lower()
        matches = 0
        
        for preferred_cert in job_preferred_certs:
            if preferred_cert.lower() in employee_certs_text:
                matches += 1
        
        if matches > 0:
            return min(matches / len(job_preferred_certs), 1.0)
        
        return 0.1  # Small bonus for any certifications
    
    def _get_matching_skills(self, job: Job, employee: Employee) -> List[str]:
        """Get list of matching skills between job and employee"""
        job_skills = self._normalize_skills(job.required_skills or [])
        employee_skills = self._normalize_skills(employee.technical_skills or [])
        
        exact_matches = job_skills.intersection(employee_skills)
        
        # Add similar skills
        similar_matches = []
        for job_skill in job_skills:
            if job_skill not in exact_matches:
                for emp_skill in employee_skills:
                    if self._calculate_skill_similarity(job_skill, emp_skill) > 0.6:
                        similar_matches.append(f"{emp_skill} (similar to {job_skill})")
                        break
        
        return list(exact_matches) + similar_matches
        
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
                score=int(match["score"]),  # Convert percentage to integer
                skills_match=match.get("skills_match", []),
                method="industry_standard"
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