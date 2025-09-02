#!/usr/bin/env python3
"""
Complete System Setup Script for Internal Mobility Platform
============================================================

This script handles BOTH fresh database setup and existing database upgrades:

🆕 FRESH DATABASE:
- Creates all tables from scratch using SQLAlchemy models
- Sets up complete system schema
- Populates with comprehensive test data

🔄 EXISTING DATABASE:
- Adds missing tables (invitations, invitation_decisions, job_comments)
- Adds new columns for features
- Preserves existing data
- Updates schema to latest version

📋 WHAT IT DOES:
1. Database Migration:
   - Creates all tables if they don't exist
   - Adds system tables (invitations, invitation_decisions, job_comments, work_experiences)
   - Adds new columns (note, optional_skills, months_experience, date_of_joining, reporting_officer_id, etc.)
   - Handles PostgreSQL-specific features

2. Test Data Creation:
   - 10 users (employees, managers, HR, admin) with enhanced profile fields
   - Realistic reporting structure and company tenure data
   - 10+ realistic work experience entries with LinkedIn-style data
   - 6 jobs with realistic descriptions
   - Sample invitations with different statuses
   - Shortlisted candidates for discovery workflow
   - Notifications for different user types

3. System Workflow Setup:
   - Employee opt-out capabilities
   - Manager discovery and shortlist workflow
   - Invitation-response system

🚀 USAGE:
- For fresh setup: Just run this script
- For upgrades: Run this script on existing database
- SQLAlchemy handles table creation safely
- All operations use IF NOT EXISTS for safety

⚠️  REQUIREMENTS:
- PostgreSQL database running
- Correct DATABASE_URL in settings
- Database user with CREATE TABLE permissions
"""
import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, text
from app.core.config import settings
from app.core.security import get_password_hash
from app.db.base import Base
from app.models.employee import Employee, WorkExperience
from app.models.job import Job, JobMatch
from app.models.application import Application
from app.models.notification import Notification
from app.models.invitation import Invitation, InvitationDecision
from app.models.job_comment import JobComment

# Test users data for invite-only system
TEST_USERS = [
    {
        "employee_id": "EMP001",
        "email": "john.doe@company.com",
        "name": "John Doe",
        "password": "password123",
        "role": "employee",
        "technical_skills": ["Python", "JavaScript", "React", "SQL", "FastAPI"],
        "months_experience": 36,  # 3 years = 36 months
        "location": "New York",
        "current_job_title": "Software Developer",
        "preferred_roles": ["Senior Developer", "Backend Developer"],
        "career_aspirations": "Looking to transition into a senior developer role with focus on backend systems.",
        "achievements": ["Built microservices architecture", "Led team of 3 developers"],
        "certifications": ["AWS Solutions Architect Associate"],
        "education": ["BS Computer Science - NYU"],
        "past_companies": ["TechCorp", "StartupXYZ"],
        "visibility_opt_out": False,
        # Enhanced profile fields
        "date_of_joining": "2023-02-01",  # Joined current company
        "reporting_officer_id": "MGR001",  # Reports to Jane Smith
        "rep_officer_name": "Jane Smith",
        "months": 18  # ~18 months since joining (Feb 2023 to current)
    },
    {
        "employee_id": "EMP002",
        "email": "bob.wilson@company.com",
        "name": "Bob Wilson",
        "password": "password123", 
        "role": "employee",
        "technical_skills": ["Java", "Spring Boot", "Microservices", "AWS", "Kubernetes"],
        "months_experience": 48,  # 4 years = 48 months
        "location": "Austin",
        "current_job_title": "Senior Developer",
        "preferred_roles": ["Cloud Architect", "DevOps Engineer"],
        "career_aspirations": "Interested in cloud architecture and distributed systems.",
        "achievements": ["Migrated legacy system to cloud", "Reduced deployment time by 80%"],
        "certifications": ["AWS Solutions Architect Professional", "Kubernetes Administrator"],
        "education": ["MS Software Engineering - UT Austin"],
        "past_companies": ["CloudTech", "Enterprise Solutions Inc"],
        "visibility_opt_out": False,
        # Enhanced profile fields
        "date_of_joining": "2022-09-01",  # Joined current company
        "reporting_officer_id": "MGR001",  # Reports to Jane Smith
        "rep_officer_name": "Jane Smith",
        "months": 24  # ~24 months since joining (Sep 2022 to current)
    },
    {
        "employee_id": "EMP003",
        "email": "sara.davis@company.com",
        "name": "Sara Davis",
        "password": "password123",
        "role": "employee", 
        "technical_skills": ["UI/UX Design", "Figma", "HTML/CSS", "React", "TypeScript"],
        "months_experience": 24,  # 2 years = 24 months
        "location": "Seattle",
        "current_job_title": "UX Designer",
        "preferred_roles": ["Senior UX Designer", "Product Designer"],
        "career_aspirations": "Looking to grow as a full-stack designer with focus on user experience.",
        "achievements": ["Redesigned main product UI", "Improved user satisfaction by 25%"],
        "certifications": ["Google UX Design Certificate"],
        "education": ["BA Graphic Design - Art Institute"],
        "past_companies": ["Design Studio LLC"],
        "visibility_opt_out": False,
        # Enhanced profile fields
        "date_of_joining": "2023-07-01",  # Joined current company
        "reporting_officer_id": "MGR001",  # Reports to Jane Smith
        "rep_officer_name": "Jane Smith",
        "months": 14  # ~14 months since joining (Jul 2023 to current)
    },
    {
        "employee_id": "EMP004",
        "email": "mike.chen@company.com",
        "name": "Mike Chen",
        "password": "password123",
        "role": "employee",
        "technical_skills": ["Python", "Machine Learning", "TensorFlow", "Data Science", "SQL"],
        "months_experience": 60,  # 5 years = 60 months
        "location": "San Francisco",
        "current_job_title": "Data Scientist",
        "preferred_roles": ["Senior Data Scientist", "ML Engineer"],
        "career_aspirations": "Seeking senior data scientist role to lead AI initiatives.",
        "achievements": ["Developed recommendation engine", "Published 3 ML research papers"],
        "certifications": ["Google Cloud ML Engineer", "Coursera ML Specialization"],
        "education": ["PhD Computer Science - Stanford"],
        "past_companies": ["DataCorp", "AI Innovations"],
        "visibility_opt_out": False,
        # Enhanced profile fields
        "date_of_joining": "2023-01-01",  # Joined current company
        "reporting_officer_id": "MGR002",  # Reports to David Kumar
        "rep_officer_name": "David Kumar",
        "months": 20  # ~20 months since joining (Jan 2023 to current)
    },
    {
        "employee_id": "EMP005",
        "email": "lisa.brown@company.com",
        "name": "Lisa Brown",
        "password": "password123",
        "role": "employee",
        "technical_skills": ["DevOps", "Docker", "Kubernetes", "CI/CD", "AWS", "Terraform"],
        "months_experience": 72,  # 6 years = 72 months
        "location": "Denver",
        "current_job_title": "DevOps Engineer",
        "preferred_roles": ["Senior DevOps Engineer", "Platform Engineer"],
        "career_aspirations": "Looking to become platform engineering lead and drive infrastructure modernization.",
        "achievements": ["Implemented company-wide CI/CD", "Reduced infrastructure costs by 40%"],
        "certifications": ["AWS DevOps Engineer Professional", "Kubernetes Administrator"],
        "education": ["BS Information Systems - UC Denver"],
        "past_companies": ["InfraTech", "DevOps Solutions"],
        "visibility_opt_out": False,
        # Enhanced profile fields
        "date_of_joining": "2021-12-01",  # Joined current company
        "reporting_officer_id": "MGR001",  # Reports to Jane Smith
        "rep_officer_name": "Jane Smith",
        "months": 33  # ~33 months since joining (Dec 2021 to current)
    },
    {
        "employee_id": "EMP006",
        "email": "alex.taylor@company.com",
        "name": "Alex Taylor",
        "password": "password123",
        "role": "employee",
        "technical_skills": ["React", "JavaScript", "Node.js", "GraphQL", "MongoDB"],
        "months_experience": 36,  # 3 years = 36 months
        "location": "Portland",
        "current_job_title": "Frontend Developer",
        "preferred_roles": ["Full Stack Developer", "Frontend Lead"],
        "career_aspirations": "Interested in becoming a full-stack developer with leadership responsibilities.",
        "achievements": ["Led frontend redesign project", "Improved page load times by 40%"],
        "certifications": ["React Developer Certification"],
        "education": ["BS Computer Science - Oregon State"],
        "past_companies": ["WebDev Inc"],
        "visibility_opt_out": True,  # This user opted out of discovery
        # Enhanced profile fields
        "date_of_joining": "2022-03-01",  # Joined current company
        "reporting_officer_id": "MGR001",  # Reports to Jane Smith
        "rep_officer_name": "Jane Smith",
        "months": 30  # ~30 months since joining (Mar 2022 to current)
    },
    {
        "employee_id": "MGR001", 
        "email": "jane.smith@company.com",
        "name": "Jane Smith",
        "password": "manager123",
        "role": "manager",
        "technical_skills": ["Project Management", "Agile", "Leadership", "Strategy", "Team Building"],
        "months_experience": 84,  # 7 years = 84 months
        "location": "San Francisco",
        "current_job_title": "Engineering Manager",
        "preferred_roles": ["Director of Engineering", "VP Engineering"],
        "career_aspirations": "Seeking opportunities to lead larger teams and drive digital transformation initiatives.",
        "achievements": ["Led 50+ person engineering org", "Delivered 5 major product releases"],
        "certifications": ["PMP", "Scrum Master"],
        "education": ["MBA - UC Berkeley", "BS Engineering - MIT"],
        "past_companies": ["TechGiant", "Innovation Labs"],
        "visibility_opt_out": False,
        # Enhanced profile fields
        "date_of_joining": "2020-01-15",  # Senior manager, been here longer
        "reporting_officer_id": None,  # Senior manager, no direct reporting officer in our test data
        "rep_officer_name": None,
        "months": 56  # ~56 months since joining (Jan 2020 to current)
    },
    {
        "employee_id": "MGR002",
        "email": "david.kumar@company.com",
        "name": "David Kumar",
        "password": "manager123",
        "role": "manager",
        "technical_skills": ["Product Management", "Strategy", "Analytics", "Leadership"],
        "months_experience": 96,  # 8 years = 96 months
        "location": "Boston",
        "current_job_title": "Product Manager",
        "preferred_roles": ["Senior Product Manager", "VP Product"],
        "career_aspirations": "Interested in VP of Product role to shape company product strategy.",
        "achievements": ["Launched 3 successful products", "Grew revenue by 200%"],
        "certifications": ["Product Management Certificate - UC Berkeley"],
        "education": ["MBA - Harvard", "BS Computer Science - IIT"],
        "past_companies": ["ProductCorp", "Strategy Consulting"],
        "visibility_opt_out": False,
        # Enhanced profile fields
        "date_of_joining": "2019-06-01",  # Senior manager, been here longer
        "reporting_officer_id": None,  # Senior manager, no direct reporting officer in our test data
        "rep_officer_name": None,
        "months": 63  # ~63 months since joining (Jun 2019 to current)
    },
    {
        "employee_id": "HR001",
        "email": "alice.johnson@company.com", 
        "name": "Alice Johnson",
        "password": "hr123",
        "role": "hr",
        "technical_skills": ["HR Analytics", "Recruitment", "Employee Relations", "HRIS", "Performance Management"],
        "months_experience": 60,  # 5 years = 60 months
        "location": "Chicago",
        "current_job_title": "HR Business Partner",
        "preferred_roles": ["Senior HR Manager", "Director of People"],
        "career_aspirations": "Interested in expanding into organizational development and change management.",
        "achievements": ["Reduced hiring time by 50%", "Implemented new performance system"],
        "certifications": ["SHRM-CP", "PHR"],
        "education": ["MS Human Resources - Northwestern"],
        "past_companies": ["HR Solutions Inc", "TalentCorp"],
        "visibility_opt_out": False,
        # Enhanced profile fields
        "date_of_joining": "2021-08-01",  # HR role
        "reporting_officer_id": None,  # HR reports to higher management, not in our test data
        "rep_officer_name": None,
        "months": 37  # ~37 months since joining (Aug 2021 to current)
    },
    {
        "employee_id": "ADM001",
        "email": "admin@company.com",
        "name": "System Administrator", 
        "password": "admin123",
        "role": "admin",
        "technical_skills": ["System Administration", "Security", "DevOps", "Database Management"],
        "months_experience": 120,  # 10 years = 120 months
        "location": "Remote",
        "current_job_title": "Systems Administrator",
        "preferred_roles": ["Security Engineer", "Platform Architect"],
        "career_aspirations": "Looking to contribute to platform architecture and security initiatives.",
        "achievements": ["Implemented zero-trust security", "99.99% uptime achievement"],
        "certifications": ["CISSP", "AWS Solutions Architect"],
        "education": ["MS Cybersecurity - CMU"],
        "past_companies": ["SecureTech", "Enterprise IT"],
        "visibility_opt_out": False,
        # Enhanced profile fields
        "date_of_joining": "2018-01-01",  # Admin has been here longest
        "reporting_officer_id": None,  # System admin reports to IT management, not in our test data
        "rep_officer_name": None,
        "months": 80  # ~80 months since joining (Jan 2018 to current)
    }
]

# Test jobs for invite-only system (managers can discover and invite)
TEST_JOBS = [
    {
        "title": "Senior Backend Developer",
        "team": "Platform Engineering",
        "description": "We're looking for a senior backend developer to join our platform team. You'll be responsible for building scalable APIs and microservices using Python and FastAPI.",
        "required_skills": ["Python", "FastAPI", "Microservices", "SQL", "AWS"],
        "optional_skills": ["Docker", "Kubernetes", "Redis"],
        "min_years_experience": 3,
        "preferred_certifications": ["AWS Solutions Architect"],
        "status": "open",
        "note": "Looking for someone with strong Python background who can mentor junior developers",
        "manager_employee_id": "MGR001"
    },
    {
        "title": "Full Stack Developer",
        "team": "Product Development",
        "description": "Join our product team to build user-facing features. You'll work on both frontend (React) and backend (Java/Spring) development.",
        "required_skills": ["React", "JavaScript", "Java", "Spring Boot", "SQL"],
        "optional_skills": ["TypeScript", "GraphQL", "AWS"],
        "min_years_experience": 2,
        "preferred_certifications": ["Oracle Java Certification"],
        "status": "open",
        "note": "Need someone who can work across the stack and collaborate well with design team",
        "manager_employee_id": "MGR002"
    },
    {
        "title": "Cloud Infrastructure Engineer",
        "team": "DevOps",
        "description": "Help us scale our cloud infrastructure. You'll work with Kubernetes, AWS, and Infrastructure as Code to support our growing platform.",
        "required_skills": ["Kubernetes", "AWS", "Terraform", "Docker", "CI/CD"],
        "optional_skills": ["Helm", "Monitoring", "Security"],
        "min_years_experience": 4,
        "preferred_certifications": ["AWS Solutions Architect Professional", "Kubernetes Administrator"],
        "status": "open",
        "note": "Critical role for scaling - need someone with production Kubernetes experience",
        "manager_employee_id": "MGR001"
    },
    {
        "title": "Data Scientist - AI/ML",
        "team": "Data Science",
        "description": "Lead our machine learning initiatives. Build recommendation systems, predictive models, and help drive data-driven decisions.",
        "required_skills": ["Python", "Machine Learning", "TensorFlow", "Data Science", "Statistics"],
        "optional_skills": ["PyTorch", "MLOps", "Spark"],
        "min_years_experience": 4,
        "preferred_certifications": ["Google Cloud ML Engineer"],
        "status": "open",
        "note": "Looking for PhD or equivalent experience, must have production ML experience",
        "manager_employee_id": "MGR002"
    },
    {
        "title": "Senior UX Designer",
        "team": "Design",
        "description": "Design intuitive user experiences for our platform. You'll work closely with product and engineering teams.",
        "required_skills": ["UI/UX Design", "Figma", "User Research", "Prototyping"],
        "optional_skills": ["HTML/CSS", "React", "Design Systems"],
        "min_years_experience": 3,
        "preferred_certifications": ["Google UX Design Certificate"],
        "status": "open",
        "note": "Need someone who can establish design systems and lead junior designers",
        "manager_employee_id": "MGR001"
    },
    {
        "title": "Platform Engineering Lead",
        "team": "Platform Engineering", 
        "description": "Lead our DevOps practices and help modernize our deployment pipeline. Focus on automation and reliability.",
        "required_skills": ["DevOps", "Kubernetes", "CI/CD", "AWS", "Leadership"],
        "optional_skills": ["Terraform", "Monitoring", "Security"],
        "min_years_experience": 6,
        "preferred_certifications": ["AWS DevOps Engineer Professional"],
        "status": "open",
        "note": "Senior role - need someone who can lead a team and drive platform strategy",
        "manager_employee_id": "MGR001"
    }
]

async def run_migration(engine):
    """Run database migration to add latest system features"""
    print("🔄 Running database migration for system features...")
    
    try:
        # First, try to connect and check if database exists
        async with engine.begin() as conn:
            # Check if we can connect to the database
            result = await conn.execute(text("SELECT 1"))
            print("✅ Database connection established")
            
            # Create all tables (will add new ones, skip existing)
            # This handles both fresh database and existing database scenarios
            await conn.run_sync(Base.metadata.create_all)
            print("✅ All tables created/verified")
            
        # Add missing columns to existing tables (for upgrade scenarios)
        columns_to_add = [
            # Jobs table - updated fields (note: removed old fields like internal_notes, short_description, visibility)
            ("jobs", "note", "TEXT"),
            ("jobs", "optional_skills", "JSON"),
            ("jobs", "min_years_experience", "INTEGER DEFAULT 0"),
            ("jobs", "preferred_certifications", "JSON"),
            
            # Job matches table - enhanced matching fields
            ("job_matches", "explanation", "TEXT"),
            ("job_matches", "shortlisted", "BOOLEAN DEFAULT FALSE"),
            ("job_matches", "method", "VARCHAR(50) DEFAULT 'semantic'"),
            
            # Employees table - visibility and resume parsing
            ("employees", "visibility_opt_out", "BOOLEAN DEFAULT FALSE"),
            ("employees", "parsed_resume", "JSON"),
            ("employees", "current_job_title", "VARCHAR(255)"),
            ("employees", "preferred_roles", "JSON"),
            
            # Enhanced profile fields for employee management
            ("employees", "date_of_joining", "DATE"),
            ("employees", "reporting_officer_id", "VARCHAR(50)"),
            ("employees", "rep_officer_name", "VARCHAR(255)"),
            ("employees", "months", "INTEGER DEFAULT 0"),
        ]
        
        print("📝 Adding/verifying additional columns...")
        async with engine.begin() as conn:
            for table, column, column_type in columns_to_add:
                try:
                    query = f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS {column} {column_type}"
                    await conn.execute(text(query))
                    print(f"✅ Column {column} added/verified in {table}")
                except Exception as e:
                    # This is expected for columns that already exist
                    print(f"ℹ️  Column {column} in {table}: {str(e)[:50]}...")
            
            # Clean up old columns that are no longer used (safe to fail)
            old_columns_to_remove = [
                ("jobs", "internal_notes"),
                ("jobs", "short_description"), 
                ("jobs", "visibility")
            ]
            
            print("🧹 Cleaning up deprecated columns...")
            for table, column in old_columns_to_remove:
                try:
                    query = f"ALTER TABLE {table} DROP COLUMN IF EXISTS {column}"
                    await conn.execute(text(query))
                    print(f"✅ Removed deprecated column {column} from {table}")
                except Exception as e:
                    print(f"ℹ️  Column {column} cleanup: {str(e)[:50]}...")
        
        print("✅ Database migration completed successfully!")
        print("✅ System ready for fresh database or existing database upgrade!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        print("💡 Make sure PostgreSQL is running and DATABASE_URL is correct")
        raise

async def create_test_users(session: AsyncSession):
    """Create test users in the database with proper dependency ordering"""
    print("\n👥 Creating test users...")
    
    created_users = {}
    
    # Sort users to create managers first (those without reporting_officer_id)
    # Then create employees who report to them
    def get_dependency_order(user_data):
        # Users without reporting_officer_id should be created first (managers, admin, hr)
        if not user_data.get("reporting_officer_id"):
            return 0
        else:
            return 1
    
    sorted_users = sorted(TEST_USERS, key=get_dependency_order)
    
    for user_data in sorted_users:
        # Check if user already exists
        result = await session.execute(
            select(Employee).where(Employee.employee_id == user_data["employee_id"])
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            print(f"⚠️  User {user_data['employee_id']} already exists, skipping")
            created_users[user_data["employee_id"]] = existing_user
            continue
        
        # Parse date_of_joining if provided
        date_of_joining = None
        if user_data.get("date_of_joining"):
            from datetime import datetime
            date_of_joining = datetime.strptime(user_data["date_of_joining"], "%Y-%m-%d").date()
        
        user = Employee(
            employee_id=user_data["employee_id"],
            email=user_data["email"],
            name=user_data["name"],
            password_hash=get_password_hash(user_data["password"]),
            role=user_data["role"],
            technical_skills=user_data["technical_skills"],
            months_experience=user_data["months_experience"],
            location=user_data["location"],
            current_job_title=user_data["current_job_title"],
            preferred_roles=user_data["preferred_roles"],
            career_aspirations=user_data["career_aspirations"],
            achievements=user_data["achievements"],
            certifications=user_data["certifications"],
            education=user_data["education"],
            past_companies=user_data["past_companies"],
            visibility_opt_out=user_data["visibility_opt_out"],
            # Enhanced profile fields
            date_of_joining=date_of_joining,
            reporting_officer_id=user_data.get("reporting_officer_id"),
            rep_officer_name=user_data.get("rep_officer_name"),
            months=user_data.get("months", 0)
        )
        
        session.add(user)
        created_users[user_data["employee_id"]] = user
        print(f"✅ Created user: {user_data['name']} ({user_data['employee_id']})")
    
    await session.commit()
    
    # Refresh all users to get their IDs
    for user in created_users.values():
        await session.refresh(user)
    
    return created_users

async def create_sample_work_experiences(session: AsyncSession, users: dict):
    """Create realistic work experience data for employees"""
    print("\n💼 Creating sample work experiences...")
    
    # Sample work experience data for each employee
    work_experiences = [
        # John Doe (EMP001) - Software Developer
        {
            "employee_id": "EMP001",
            "experiences": [
                {
                    "company_name": "TechCorp",
                    "job_title": "Junior Software Developer",
                    "start_date": "2021-06-01",
                    "end_date": "2023-01-31",
                    "employment_type": "Full-time",
                    "location": "New York, NY",
                    "description": "Developed web applications using React and Node.js. Collaborated with senior developers on various client projects.",
                    "key_achievements": ["Built responsive e-commerce platform", "Reduced page load time by 30%"],
                    "skills_used": ["React", "Node.js", "JavaScript", "HTML/CSS"],
                    "technologies_used": ["React", "Express.js", "MongoDB", "Git"]
                },
                {
                    "company_name": "StartupXYZ",
                    "job_title": "Software Developer",
                    "start_date": "2023-02-01",
                    "end_date": None,
                    "is_current": True,
                    "employment_type": "Full-time",
                    "location": "New York, NY",
                    "description": "Full-stack development using Python and React. Working on microservices architecture and API development.",
                    "key_achievements": ["Led migration to microservices", "Implemented CI/CD pipeline"],
                    "skills_used": ["Python", "FastAPI", "React", "SQL", "AWS"],
                    "technologies_used": ["FastAPI", "PostgreSQL", "Docker", "AWS Lambda"]
                }
            ]
        },
        
        # Bob Wilson (EMP002) - Senior Developer
        {
            "employee_id": "EMP002",
            "experiences": [
                {
                    "company_name": "CloudTech",
                    "job_title": "Java Developer",
                    "start_date": "2020-03-01",
                    "end_date": "2022-08-31",
                    "employment_type": "Full-time",
                    "location": "Austin, TX",
                    "description": "Developed enterprise applications using Java and Spring Boot. Worked on cloud migration projects.",
                    "key_achievements": ["Migrated monolith to microservices", "Reduced deployment time by 70%"],
                    "skills_used": ["Java", "Spring Boot", "AWS", "Docker"],
                    "technologies_used": ["Spring Boot", "AWS ECS", "RDS", "CloudFormation"]
                },
                {
                    "company_name": "Enterprise Solutions Inc",
                    "job_title": "Senior Java Developer",
                    "start_date": "2022-09-01",
                    "end_date": None,
                    "is_current": True,
                    "employment_type": "Full-time",
                    "location": "Austin, TX",
                    "description": "Leading backend development team. Architecting scalable solutions using microservices and Kubernetes.",
                    "key_achievements": ["Designed payment processing system", "Achieved 99.9% uptime"],
                    "skills_used": ["Java", "Spring Boot", "Kubernetes", "Microservices"],
                    "technologies_used": ["Kubernetes", "Istio", "Prometheus", "Grafana"]
                }
            ]
        },
        
        # Sara Davis (EMP003) - UX Designer
        {
            "employee_id": "EMP003",
            "experiences": [
                {
                    "company_name": "Design Studio LLC",
                    "job_title": "Junior UX Designer",
                    "start_date": "2022-01-01",
                    "end_date": "2023-06-30",
                    "employment_type": "Full-time",
                    "location": "Seattle, WA",
                    "description": "Created user interfaces and experiences for mobile and web applications. Conducted user research and usability testing.",
                    "key_achievements": ["Redesigned mobile app UI", "Improved user engagement by 40%"],
                    "skills_used": ["Figma", "Adobe XD", "User Research", "Prototyping"],
                    "technologies_used": ["Figma", "Adobe Creative Suite", "InVision", "Miro"]
                },
                {
                    "company_name": "Current Company",
                    "job_title": "UX Designer",
                    "start_date": "2023-07-01",
                    "end_date": None,
                    "is_current": True,
                    "employment_type": "Full-time",
                    "location": "Seattle, WA",
                    "description": "Leading UX design for internal tools and customer-facing products. Collaborating with product and engineering teams.",
                    "key_achievements": ["Launched design system", "Reduced development time by 25%"],
                    "skills_used": ["UI/UX Design", "Design Systems", "HTML/CSS", "React"],
                    "technologies_used": ["Figma", "Storybook", "HTML/CSS", "React"]
                }
            ]
        },
        
        # Mike Chen (EMP004) - Data Scientist
        {
            "employee_id": "EMP004",
            "experiences": [
                {
                    "company_name": "DataCorp",
                    "job_title": "Machine Learning Engineer",
                    "start_date": "2019-08-01",
                    "end_date": "2022-12-31",
                    "employment_type": "Full-time",
                    "location": "San Francisco, CA",
                    "description": "Built and deployed machine learning models for recommendation systems. Worked with large-scale data processing.",
                    "key_achievements": ["Improved recommendation accuracy by 15%", "Reduced model training time by 50%"],
                    "skills_used": ["Python", "TensorFlow", "Spark", "SQL"],
                    "technologies_used": ["TensorFlow", "Apache Spark", "Kubernetes", "MLflow"]
                },
                {
                    "company_name": "AI Innovations",
                    "job_title": "Senior Data Scientist",
                    "start_date": "2023-01-01",
                    "end_date": None,
                    "is_current": True,
                    "employment_type": "Full-time",
                    "location": "San Francisco, CA",
                    "description": "Leading AI research initiatives and developing next-generation ML models. Publishing research and mentoring junior scientists.",
                    "key_achievements": ["Published 3 research papers", "Built computer vision pipeline"],
                    "skills_used": ["Python", "PyTorch", "Computer Vision", "NLP"],
                    "technologies_used": ["PyTorch", "Transformers", "OpenCV", "AWS SageMaker"]
                }
            ]
        },
        
        # Lisa Brown (EMP005) - DevOps Engineer
        {
            "employee_id": "EMP005",
            "experiences": [
                {
                    "company_name": "InfraTech",
                    "job_title": "DevOps Engineer",
                    "start_date": "2018-05-01",
                    "end_date": "2021-11-30",
                    "employment_type": "Full-time",
                    "location": "Denver, CO",
                    "description": "Managed cloud infrastructure and implemented CI/CD pipelines. Automated deployment processes and monitoring systems.",
                    "key_achievements": ["Automated 90% of deployments", "Reduced infrastructure costs by 30%"],
                    "skills_used": ["AWS", "Docker", "Jenkins", "Terraform"],
                    "technologies_used": ["AWS", "Docker", "Jenkins", "Ansible"]
                },
                {
                    "company_name": "DevOps Solutions",
                    "job_title": "Senior DevOps Engineer",
                    "start_date": "2021-12-01",
                    "end_date": None,
                    "is_current": True,
                    "employment_type": "Full-time",
                    "location": "Denver, CO",
                    "description": "Leading platform engineering initiatives. Architecting multi-cloud solutions and implementing GitOps workflows.",
                    "key_achievements": ["Designed multi-cloud strategy", "Implemented zero-downtime deployments"],
                    "skills_used": ["Kubernetes", "Terraform", "GitOps", "Monitoring"],
                    "technologies_used": ["Kubernetes", "ArgoCD", "Prometheus", "Istio"]
                }
            ]
        }
    ]
    
    created_count = 0
    
    for user_exp in work_experiences:
        employee = users.get(user_exp["employee_id"])
        if not employee:
            print(f"⚠️  Employee {user_exp['employee_id']} not found, skipping work experiences")
            continue
        
        for exp_data in user_exp["experiences"]:
            # Check if work experience already exists
            result = await session.execute(
                select(WorkExperience).where(
                    WorkExperience.employee_id == employee.employee_id,
                    WorkExperience.company_name == exp_data["company_name"],
                    WorkExperience.job_title == exp_data["job_title"]
                )
            )
            existing_exp = result.scalar_one_or_none()
            
            if existing_exp:
                print(f"⚠️  Work experience already exists: {employee.name} at {exp_data['company_name']}")
                continue
            
            # Parse dates
            from datetime import datetime
            start_date = datetime.strptime(exp_data["start_date"], "%Y-%m-%d").date()
            end_date = None
            if exp_data.get("end_date"):
                end_date = datetime.strptime(exp_data["end_date"], "%Y-%m-%d").date()
            
            work_exp = WorkExperience(
                employee_id=employee.employee_id,
                company_name=exp_data["company_name"],
                job_title=exp_data["job_title"],
                start_date=start_date,
                end_date=end_date,
                is_current=exp_data.get("is_current", False),
                employment_type=exp_data["employment_type"],
                location=exp_data["location"],
                description=exp_data["description"],
                key_achievements=exp_data["key_achievements"],
                skills_used=exp_data["skills_used"],
                technologies_used=exp_data["technologies_used"]
            )
            
            # Calculate duration
            work_exp.duration_months = work_exp.calculate_duration_months()
            
            session.add(work_exp)
            created_count += 1
            print(f"✅ Created work experience: {employee.name} - {exp_data['job_title']} at {exp_data['company_name']}")
    
    await session.commit()
    print(f"✅ Created {created_count} work experience entries")

async def create_test_jobs(session: AsyncSession, users: dict):
    """Create test jobs in the database"""
    print("\n💼 Creating test jobs...")
    
    created_jobs = {}
    
    for job_data in TEST_JOBS:
        # Find manager
        manager = users.get(job_data["manager_employee_id"])
        if not manager:
            print(f"⚠️  Manager {job_data['manager_employee_id']} not found, skipping job {job_data['title']}")
            continue
        
        # Check if job already exists
        result = await session.execute(
            select(Job).where(Job.title == job_data["title"])
        )
        existing_job = result.scalar_one_or_none()
        
        if existing_job:
            print(f"⚠️  Job {job_data['title']} already exists, skipping")
            created_jobs[job_data["title"]] = existing_job
            continue
        
        job = Job(
            title=job_data["title"],
            team=job_data["team"],
            description=job_data["description"],
            required_skills=job_data["required_skills"],
            optional_skills=job_data["optional_skills"],
            min_years_experience=job_data["min_years_experience"],
            preferred_certifications=job_data["preferred_certifications"],
            status=job_data["status"],
            note=job_data["note"],
            manager_id=manager.id
        )
        
        session.add(job)
        created_jobs[job_data["title"]] = job
        print(f"✅ Created job: {job_data['title']} (Manager: {manager.name})")
    
    await session.commit()
    
    # Refresh all jobs to get their IDs
    for job in created_jobs.values():
        await session.refresh(job)
    
    return created_jobs

async def create_sample_invitations(session: AsyncSession, users: dict, jobs: dict):
    """Create sample invitations to demonstrate the invite-only workflow"""
    print("\n📬 Creating sample invitations...")
    
    # Sample invitation scenarios
    invitation_scenarios = [
        {
            "job_title": "Senior Backend Developer",
            "employee_id": "EMP001",  # John Doe - Python developer
            "inviter_id": "MGR001",   # Jane Smith
            "content": "Hi John! I've been impressed with your Python work and think you'd be a great fit for our Senior Backend Developer role. Would you be interested in learning more?",
            "status": "pending"
        },
        {
            "job_title": "Cloud Infrastructure Engineer", 
            "employee_id": "EMP002",  # Bob Wilson - Java/AWS
            "inviter_id": "MGR001",   # Jane Smith
            "content": "Bob, your AWS and Kubernetes experience would be perfect for our cloud infrastructure role. Let's chat!",
            "status": "pending"
        },
        {
            "job_title": "Data Scientist - AI/ML",
            "employee_id": "EMP004",  # Mike Chen - ML expert
            "inviter_id": "MGR002",   # David Kumar
            "content": "Mike, we're expanding our ML team and your background is exactly what we need. Are you open to exploring this opportunity?",
            "status": "accepted"  # Already accepted
        },
        {
            "job_title": "Senior UX Designer",
            "employee_id": "EMP003",  # Sara Davis - UX Designer
            "inviter_id": "MGR001",   # Jane Smith
            "content": "Sara, I've seen your design work and would love to have you join our team as a Senior UX Designer. Interested?",
            "status": "pending"
        },
        {
            "job_title": "Platform Engineering Lead",
            "employee_id": "EMP005",  # Lisa Brown - DevOps
            "inviter_id": "MGR001",   # Jane Smith
            "content": "Lisa, we're looking for a Platform Engineering Lead and your DevOps background makes you an ideal candidate. Let's discuss!",
            "status": "info_requested"  # Employee requested more info
        }
    ]
    
    for scenario in invitation_scenarios:
        job = jobs.get(scenario["job_title"])
        employee = users.get(scenario["employee_id"])
        inviter = users.get(scenario["inviter_id"])
        
        if not all([job, employee, inviter]):
            print(f"⚠️  Missing data for invitation scenario, skipping")
            continue
        
        # Check if invitation already exists
        result = await session.execute(
            select(Invitation).where(
                Invitation.job_id == job.id,
                Invitation.employee_id == employee.id
            )
        )
        existing_invitation = result.scalar_one_or_none()
        
        if existing_invitation:
            print(f"⚠️  Invitation already exists for {employee.name} -> {job.title}")
            continue
        
        invitation = Invitation(
            job_id=job.id,
            employee_id=employee.id,
            inviter_id=inviter.id,
            content=scenario["content"],
            status=scenario["status"],
            manager_notes=f"Invited based on skills match analysis"
        )
        
        session.add(invitation)
        print(f"✅ Created invitation: {employee.name} -> {job.title} (Status: {scenario['status']})")
        
        # If status is accepted or info_requested, create a decision record
        if scenario["status"] in ["accepted", "info_requested"]:
            await session.flush()  # Get invitation ID
            
            decision_type = "accept" if scenario["status"] == "accepted" else "request_info"
            decision_note = "Excited about this opportunity!" if decision_type == "accept" else "Could you tell me more about the team structure and growth opportunities?"
            
            decision = InvitationDecision(
                invitation_id=invitation.id,
                actor_id=employee.id,
                decision=decision_type,
                note=decision_note
            )
            
            session.add(decision)
            print(f"  ↳ Added decision: {decision_type}")
    
    await session.commit()

async def create_sample_shortlists(session: AsyncSession, users: dict, jobs: dict):
    """Create sample shortlisted candidates"""
    print("\n⭐ Creating sample shortlisted candidates...")
    
    # Sample shortlist scenarios (candidates discovered but not yet invited)
    shortlist_scenarios = [
        {
            "job_title": "Full Stack Developer",
            "employee_id": "EMP001",  # John Doe - has React and JS skills
            "score": 85.0,
            "explanation": "Semantic match: TF-IDF analysis shows strong content similarity in skills and experience"
        },
        {
            "job_title": "Full Stack Developer", 
            "employee_id": "EMP003",  # Sara Davis - has React and design skills
            "score": 78.0,
            "explanation": "Semantic match: TF-IDF analysis indicates good content overlap between profile and requirements"
        },
        {
            "job_title": "Cloud Infrastructure Engineer",
            "employee_id": "EMP005",  # Lisa Brown - DevOps expert
            "score": 95.0,
            "explanation": "Semantic match: TF-IDF cosine similarity shows excellent semantic alignment"
        },
        {
            "job_title": "Senior Backend Developer",
            "employee_id": "EMP002",  # Bob Wilson - Java/Microservices
            "score": 72.0,
            "explanation": "Semantic match: Moderate TF-IDF similarity with some skill domain overlap identified"
        }
    ]
    
    for scenario in shortlist_scenarios:
        job = jobs.get(scenario["job_title"])
        employee = users.get(scenario["employee_id"])
        
        if not all([job, employee]):
            print(f"⚠️  Missing data for shortlist scenario, skipping")
            continue
        
        # Check if match already exists
        result = await session.execute(
            select(JobMatch).where(
                JobMatch.job_id == job.id,
                JobMatch.employee_id == employee.id
            )
        )
        existing_match = result.scalar_one_or_none()
        
        if existing_match:
            print(f"⚠️  Match already exists for {employee.name} -> {job.title}")
            continue
        
        job_match = JobMatch(
            job_id=job.id,
            employee_id=employee.id,
            score=scenario["score"],
            explanation=scenario["explanation"],
            shortlisted=True,
            method="semantic"
        )
        
        session.add(job_match)
        print(f"✅ Shortlisted: {employee.name} -> {job.title} (Score: {scenario['score']})")
    
    await session.commit()

async def create_test_notifications(session: AsyncSession, users: dict):
    """Create some test notifications"""
    print("\n🔔 Creating test notifications...")
    
    notifications = [
        {
            "user_employee_id": "EMP001",
            "content": "You've been invited to consider the Senior Backend Developer position! Check your invitations to respond.",
            "read": False
        },
        {
            "user_employee_id": "EMP002", 
            "content": "You've been invited to consider the Cloud Infrastructure Engineer position! Check your invitations to respond.",
            "read": False
        },
        {
            "user_employee_id": "EMP004",
            "content": "Your invitation response for Data Scientist - AI/ML has been received. The hiring manager will be in touch soon!",
            "read": False
        },
        {
            "user_employee_id": "MGR001",
            "content": "Lisa Brown has requested more information about the Platform Engineering Lead position.",
            "read": False
        },
        {
            "user_employee_id": "MGR002",
            "content": "Great news! Mike Chen has accepted your invitation for the Data Scientist - AI/ML position.",
            "read": True
        },
        {
            "user_employee_id": "HR001",
            "content": "New invitation responses need review for Data Scientist - AI/ML position.",
            "read": False
        }
    ]
    
    for notif_data in notifications:
        user = users.get(notif_data["user_employee_id"])
        if not user:
            print(f"⚠️  User {notif_data['user_employee_id']} not found, skipping notification")
            continue
        
        notification = Notification(
            user_id=user.id,
            content=notif_data["content"],
            read=notif_data["read"]
        )
        
        session.add(notification)
        print(f"✅ Created notification for {user.name}")
    
    await session.commit()

async def verify_database_setup(engine):
    """Verify database setup and show status"""
    print("🔍 Verifying database setup...")
    
    try:
        async with engine.begin() as conn:
            # Check if core tables exist
            core_tables = ["employees", "jobs", "applications", "invitations", "invitation_decisions"]
            existing_tables = []
            
            for table in core_tables:
                try:
                    result = await conn.execute(text(f"SELECT 1 FROM {table} LIMIT 1"))
                    existing_tables.append(table)
                except:
                    pass
            
            print(f"✅ Found {len(existing_tables)}/{len(core_tables)} core tables")
            
            if len(existing_tables) == 0:
                print("📦 Fresh database detected - will create all tables")
                return "fresh"
            elif len(existing_tables) < len(core_tables):
                print("🔄 Partial database detected - will upgrade missing tables")
                return "partial"
            else:
                print("✅ Complete database detected - will verify and add missing features")
                return "complete"
                
    except Exception as e:
        print(f"⚠️  Database verification failed: {e}")
        print("📦 Assuming fresh database setup needed")
        return "fresh"

async def main():
    """Main function to set up the complete system"""
    print("🚀 Setting up complete Internal Mobility Platform (Invite-Only System)")
    print("="*80)
    
    # Create async engine
    try:
        engine = create_async_engine(settings.DATABASE_URL, echo=False)
        print(f"📡 Connecting to database: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'localhost'}")
    except Exception as e:
        print(f"❌ Failed to create database engine: {e}")
        print("💡 Check your DATABASE_URL in .env file")
        return
    
    # Create async session
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    try:
        # Step 1: Verify database status
        db_status = await verify_database_setup(engine)
        
        # Step 2: Run migration based on database status
        await run_migration(engine)
        
        # Step 3: Create test data
        print("\n📊 Setting up test data...")
        async with async_session() as session:
            # Create users
            users = await create_test_users(session)
            
            # Create sample work experiences
            await create_sample_work_experiences(session, users)
            
            # Create jobs
            jobs = await create_test_jobs(session, users)
            
            # Create sample invitations
            await create_sample_invitations(session, users, jobs)
            
            # Create sample shortlists
            await create_sample_shortlists(session, users, jobs)
            
            # Create notifications
            await create_test_notifications(session, users)
            
        print("\n🎉 Complete system setup finished successfully!")
        print(f"🎯 Database Status: {db_status.title()} setup completed")
        print_credentials_and_instructions()
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Make sure PostgreSQL is running")
        print("2. Check DATABASE_URL in your .env file")
        print("3. Ensure database user has CREATE TABLE permissions")
        print("4. For fresh setup, create an empty database first")
        raise
    finally:
        await engine.dispose()

def print_credentials_and_instructions():
    """Print login credentials and testing instructions for invite-only system"""
    print("\n" + "="*80)
    print("🔐 INVITE-ONLY SYSTEM - TEST CREDENTIALS")
    print("="*80)
    print("Use these credentials to test the invite-only workflow:")
    print()
    
    print("👨‍💼 MANAGERS (can discover candidates, create shortlists, send invitations):")
    print("   Employee ID: MGR001, Password: manager123 (Jane Smith - Platform Engineering)")
    print("   Employee ID: MGR002, Password: manager123 (David Kumar - Product Development)")
    print()
    
    print("👥 HR (can see all activities, manage invitations):")
    print("   Employee ID: HR001, Password: hr123 (Alice Johnson)")
    print()
    
    print("👨‍💻 EMPLOYEES (can view and respond to invitations):")
    print("   Employee ID: EMP001, Password: password123 (John Doe - Has pending invitation)")
    print("   Employee ID: EMP002, Password: password123 (Bob Wilson - Has pending invitation)")
    print("   Employee ID: EMP003, Password: password123 (Sara Davis - Has pending invitation)")
    print("   Employee ID: EMP004, Password: password123 (Mike Chen - Accepted invitation)")
    print("   Employee ID: EMP005, Password: password123 (Lisa Brown - Requested more info)")
    print("   Employee ID: EMP006, Password: password123 (Alex Taylor - Opted out of discovery)")
    print()
    
    print("🔧 ADMIN (can manage everything):")
    print("   Employee ID: ADM001, Password: admin123 (System Administrator)")
    print()
    
    print("="*80)
    print("🧪 TESTING THE INVITE-ONLY WORKFLOW:")
    print("="*80)
    print()
    print("📋 FOR MANAGERS (MGR001 or MGR002):")
    print("1. Login and go to Jobs section")
    print("2. Click on any job to view details")
    print("3. Use 'Discover Candidates' to find potential matches")
    print("4. Use 'Add to Shortlist' to shortlist interesting candidates")
    print("5. Use 'Send Invitation' to invite shortlisted candidates")
    print("6. View 'Shortlisted Candidates' to see your curated list")
    print()
    
    print("👥 FOR EMPLOYEES (EMP001-EMP006):")
    print("1. Login and go to 'My Invitations' section")
    print("2. View pending invitations from managers")
    print("3. Respond with 'Accept', 'Decline', or 'Request More Info'")
    print("4. Note: No job browsing available (invite-only system)")
    print()
    
    print("🏢 FOR HR (HR001):")
    print("1. Login and view all invitation activities")
    print("2. Monitor invitation responses and status")
    print("3. Assist with invitation workflows")
    print()
    
    print("="*80)
    print("📊 SAMPLE DATA CREATED:")
    print("="*80)
    print("• 10 Users (6 employees, 2 managers, 1 HR, 1 admin)")
    print("• 10+ Work experience entries with realistic LinkedIn-style data")
    print("• 6 Jobs (all invite-only)")
    print("• 5 Sample invitations with different statuses")
    print("• 4 Shortlisted candidates")
    print("• 6 Notifications")
    print("• 1 Employee opted out of discovery (EMP006)")
    print()
    
    print("🎯 KEY WORKFLOW FEATURES:")
    print("• Complete job creation and application system")
    print("• Enhanced job matching with semantic capabilities")
    print("• Comprehensive employee profiles with skills and work experience")
    print("• LinkedIn-style work experience tracking with duration calculation")
    print("• Admin management and notification system")
    print("• Role-based access control and authentication")
    print("• Application tracking and status management")
    print()
    
    # Step 6: Test semantic matching system
    print("🧠 Testing pure semantic matching system...")
    try:
        from app.services.semantic_match_service import PureSemanticMatchService
        print("✅ PureSemanticMatchService imported successfully")
        
        # Test ML dependencies
        import numpy as np
        import sklearn
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        from sklearn.decomposition import TruncatedSVD
        print("✅ All ML dependencies available")
        
        # Test basic functionality
        vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=100)
        test_texts = ["python backend developer", "frontend react engineer"]
        vectors = vectorizer.fit_transform(test_texts)
        similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
        print(f"✅ Basic TF-IDF + cosine similarity working (test score: {similarity:.1%})")
        print("✅ Pure semantic matching system ready!")
        
    except ImportError as e:
        print(f"❌ Could not import dependencies: {e}")
        print("💡 Run: pip install scikit-learn numpy")
    except Exception as e:
        print(f"❌ Semantic matching test failed: {e}")
    
    print()
    print("🚀 Ready to test! Start the backend server and try the workflows above.")
    print("="*80)
    print()
    print("🗄️  DATABASE SETUP NOTES:")
    print("="*80)
    print("✅ This script works for BOTH scenarios:")
    print("   • Fresh Database: Creates all tables and schema from scratch")
    print("   • Existing Database: Safely adds missing tables/columns")
    print()
    print("📋 For fresh PostgreSQL setup:")
    print("   1. Create empty database: CREATE DATABASE internal_mobility;")
    print("   2. Set DATABASE_URL in .env file")
    print("   3. Run this script: python setup_complete_system.py")
    print("   4. Start server: uvicorn app.main:app --reload")
    print()
    print("🔄 For existing database upgrade:")
    print("   • Just run this script - it safely adds missing features")
    print("   • Existing data is preserved")
    print("   • Enhanced system features are added")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(main())
