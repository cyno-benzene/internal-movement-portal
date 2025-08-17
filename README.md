# Internal Movement Portal

A role-based HR management system for internal job postings and employee movement tracking.

## Tech Stack

- **Backend**: FastAPI + PostgreSQL
- **Frontend**: Angular 18+ + Material UI
- **Authentication**: JWT-based role system

## Features

- **Role-based Access**: HR, Manager, Employee dashboards
- **Job Management**: Create, list, and match positions
- **AI Matching**: Intelligent candidate-job matching
- **Invitation System**: Role-aware employee invitations
- **Notifications**: Real-time updates and navigation
- **Dashboard Analytics**: Company statistics and metrics

## Quick Start

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
ng serve
```

## Access

- **Backend API**: http://localhost:8000
- **Frontend**: http://localhost:4200
- **API Docs**: http://localhost:8000/docs

## Roles

- **HR**: Full access to user management and analytics
- **Manager**: Job creation and team management
- **Employee**: Profile management and job applications
