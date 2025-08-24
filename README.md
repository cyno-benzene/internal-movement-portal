# Internal Movement Portal

A role-based HR management system for internal job postings and employee movement tracking with **pure semantic matching** using industry-standard ML algorithms.

## Tech Stack

- **Backend**: FastAPI + PostgreSQL + SQLAlchemy
- **Frontend**: Angular 18+ + Material UI  
- **Authentication**: JWT-based role system
- **ML Matching**: Pure TF-IDF + LSA + Cosine Similarity

## Features

- **Role-based Access**: HR, Manager, Employee dashboards
- **Invite-Only Jobs**: Curated job discovery and invitation system
- **Semantic Matching**: TF-IDF + cosine similarity 
- **Shortlisting Workflow**: Manager-driven candidate curation
- **Invitation System**: Role-aware employee invitations with response workflow
- **Notifications**: Real-time updates and navigation
- **Dashboard Analytics**: Company statistics and metrics

## 🚀 Fresh Database Setup

### Prerequisites
```bash
# Create PostgreSQL database
createdb imp_db

# Or using psql:
psql -c "CREATE DATABASE imp_db;"
```

### 1. Environment Configuration
Create `.env` file in `/backend/` directory:
```env
# Database Configuration
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/imp_db

# JWT Configuration  
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application Configuration
DEBUG=True
```

### 2. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 3. Validate Setup
```bash
python validate_setup.py
```

Expected output for ready setup:
```
🚀 Internal Mobility Platform - Setup Validator
============================================================
✅ Environment Config: Working
✅ Required Packages: All installed (including ML dependencies)
✅ Database Connection: Connected  

🎉 All checks passed! Ready to run setup_complete_system.py
```

### 4. Initialize Database
```bash
python setup_complete_system.py
```

This creates:
- ✅ Complete database schema with all tables
- ✅ Test users with profiles
- ✅ Sample invite-only jobs
- ✅ Invitation workflow test data

### 5. Start Application
```bash
# Backend
uvicorn app.main:app --reload

# Frontend (new terminal)
cd ../frontend
npm install
ng serve
```

## 🔐 Test Credentials (After Setup)

**Managers** (can discover candidates, create shortlists, send invitations):
- Employee ID: `MGR001`, Password: `manager123` (Jane Smith - Platform Engineering)
- Employee ID: `MGR002`, Password: `manager123` (David Kumar - Product Development)

**HR** (can see all activities, manage invitations):
- Employee ID: `HR001`, Password: `hr123` (Alice Johnson)

**Employees** (can view and respond to invitations):
- Employee ID: `EMP001`, Password: `password123` (John Doe - Has pending invitation)
- Employee ID: `EMP002`, Password: `password123` (Bob Wilson)
- Employee ID: `EMP003`, Password: `password123` (Sara Davis)

**Admin** (can manage everything):
- Employee ID: `ADM001`, Password: `admin123` (System Administrator)

## 🧠 The core matching system

This system uses:

- **TF-IDF Vectorization**: Converts job descriptions and profiles to mathematical vectors
- **LSA (Latent Semantic Analysis)**: Dimensionality reduction for semantic understanding  
- **Cosine Similarity**: Pure mathematical similarity scoring

## 🌐 Access URLs

- **Backend API**: http://localhost:8000
- **Frontend**: http://localhost:4200  
- **API Documentation**: http://localhost:8000/docs
- **Database Admin**: Use your preferred PostgreSQL client

## 📋 Testing the Invite-Only Workflow

### For Managers (MGR001 or MGR002):
1. Login and go to Jobs section
2. Click on any job to view details
3. Use 'Discover Candidates' to find semantic matches
4. Use 'Add to Shortlist' to shortlist interesting candidates
5. Use 'Send Invitation' to invite shortlisted candidates
6. View 'Shortlisted Candidates' to see your curated list

### For Employees (EMP001, EMP002, etc.):
1. Login to see your dashboard
2. Check 'My Invitations' for pending invitations
3. View invitation details and job requirements
4. Respond: Accept, Request More Info, or Decline
5. Track invitation status and manager responses

### For HR (HR001):
1. Login to access HR dashboard
2. View all company job activities
3. Monitor invitation workflows
4. Access analytics and reports
5. Manage employee profiles and permissions

## 🔧 Development

### Backend Development
```bash
cd backend
python -m pytest  # Run tests
python validate_setup.py  # Validate environment
```

### Frontend Development  
```bash
cd frontend
ng test  # Run tests
ng build  # Build for production
```

## 📊 System Architecture

- **Invite-Only Jobs**: Jobs are not publicly visible, employees only see invited opportunities
- **Role-Based Security**: JWT authentication with proper authorization
- **Async Database**: SQLAlchemy async for high performance
- **Real-time Notifications**: Keep users informed of invitation activities

---

**Ready for production deployment with industry-standard ML matching! 🎉**
