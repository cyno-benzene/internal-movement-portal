# Database Setup Guide

This directory contains scripts to set up the Internal Mobility Platform database for both fresh installations and existing database upgrades.

## 🚀 Quick Start

### For Fresh Database Setup:

1. **Ensure PostgreSQL is running**
2. **Create empty database:**
   ```sql
   CREATE DATABASE imp_db;
   CREATE USER imp_user WITH PASSWORD 'password';
   GRANT USAGE ON SCHEMA public TO imp_user;
   GRANT CREATE ON SCHEMA public TO imp_user;
   ALTER DATABASE imp_db OWNER TO imp_user;
   GRANT ALL PRIVILEGES ON DATABASE imp_db TO imp_user;
   ```

3. **Configure environment:**
   ```bash
   # Create .env file
   DATABASE_URL=postgresql+asyncpg://mobility_user:your_password@localhost/internal_mobility
   SECRET_KEY=your-super-secret-key-here
   ```

4. **Run setup:**
   ```bash
   # Validate environment first (optional)
   python validate_setup.py
   
   # Run complete setup
   python setup_complete_system.py
   ```

### For Existing Database Upgrade:

Simply run the setup script - it safely adds missing features without affecting existing data:

```bash
python setup_complete_system.py
```

## 📋 What Gets Created

### Database Schema:
- **Core Tables**: employees, jobs, applications, notifications
- **Invite-Only Tables**: invitations, invitation_decisions  
- **Enhanced Columns**: visibility controls, shortlisting, job details

### Test Data:
- **10 Users**: 6 employees, 2 managers, 1 HR, 1 admin
- **6 Jobs**: All configured for invite-only workflow
- **5 Invitations**: Different statuses (pending, accepted, info_requested)
- **4 Shortlisted**: Candidates discovered but not yet invited
- **6 Notifications**: Realistic notification scenarios

## 🔧 Scripts Overview

| Script | Purpose |
|--------|---------|
| `setup_complete_system.py` | **Main script** - Complete database setup + test data |
| `validate_setup.py` | Environment validation and connection testing |
| `migrate_db.py` | Legacy - Basic migration only |
| `add_columns.py` | Legacy - Column additions only |

## 🎯 Invite-Only System Features

The setup creates a complete invite-only internal mobility platform:

### Key Differences from Job Board:
- ❌ Employees cannot browse jobs
- ✅ Managers discover candidates using search
- ✅ Managers create shortlists of potential candidates  
- ✅ Managers send personalized invitations
- ✅ Employees respond to invitations (accept/decline/request info)
- ✅ Jobs have `visibility='invite_only'`
- ✅ Employee opt-out from discovery

### Workflow:
1. **Manager**: Creates invite-only job
2. **Manager**: Discovers candidates via skills/criteria search
3. **Manager**: Shortlists interesting candidates
4. **Manager**: Sends personalized invitations
5. **Employee**: Receives invitation notification
6. **Employee**: Responds (accept/decline/request more info)
7. **Manager**: Proceeds with hiring process

## 🔐 Test Credentials

After setup, use these credentials to test:

**Managers** (can discover & invite):
- `MGR001` / `manager123` (Jane Smith)
- `MGR002` / `manager123` (David Kumar)

**Employees** (receive invitations):
- `EMP001` / `password123` (John Doe - has pending invitation)
- `EMP002` / `password123` (Bob Wilson - has pending invitation)
- `EMP003` / `password123` (Sara Davis - has pending invitation)
- `EMP004` / `password123` (Mike Chen - accepted invitation)
- `EMP005` / `password123` (Lisa Brown - requested more info)

**HR** (monitor activities):
- `HR001` / `hr123` (Alice Johnson)

**Admin** (full access):
- `ADM001` / `admin123` (System Administrator)

## 🛠️ Troubleshooting

### Common Issues:

1. **Connection Failed**: 
   - Check PostgreSQL is running
   - Verify DATABASE_URL in .env
   - Ensure database exists

2. **Permission Denied**:
   - Grant CREATE privileges to database user
   - Check user has access to database

3. **Import Errors**:
   - Install requirements: `pip install -r requirements.txt`
   - Check Python path includes app directory

4. **Column Already Exists**:
   - Normal for existing databases
   - Script safely handles existing columns

### Getting Help:

Run the validation script to diagnose issues:
```bash
python validate_setup.py
```

This will check:
- Environment configuration
- Required packages
- Database connectivity
- PostgreSQL version

## 🔄 SQLAlchemy Features

The setup leverages SQLAlchemy's powerful features:

- **`create_all()`**: Creates all tables safely (skips existing)
- **`IF NOT EXISTS`**: PostgreSQL-safe column additions
- **Async Operations**: Non-blocking database operations
- **Relationship Management**: Proper foreign key constraints
- **Type Safety**: Strong typing with Pydantic models

This ensures the script works reliably for both fresh databases and upgrades without data loss.
