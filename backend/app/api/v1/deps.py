from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.core.security import verify_token
from app.models.employee import Employee

from app.core.logging_config import get_api_logger

security = HTTPBearer()
logger = get_api_logger()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Employee:
    token = credentials.credentials
    payload = verify_token(token)
    
    user_id = payload.get("sub")
    if user_id is None:
        logger.warning("Token verification failed: 'sub' not in payload")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    result = await db.execute(select(Employee).where(Employee.id == user_id))
    user = result.scalar_one_or_none()
    
    if user is None:
        logger.warning(f"User not found for ID: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    logger.info(f"Authenticated user: {user.email} (Role: {user.role})")
    return user

def require_role(allowed_roles: list[str]):
    def role_checker(current_user: Employee = Depends(get_current_user)) -> Employee:
        if current_user.role not in allowed_roles:
            logger.warning(
                f"Authorization failed for user {current_user.email}. "
                f"Required roles: {allowed_roles}, User role: {current_user.role}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {', '.join(allowed_roles)}"
            )
        return current_user
    return role_checker

# Convenience functions for specific roles
def require_admin():
    return require_role(["admin"])

def require_hr_or_admin():
    return require_role(["hr", "admin"])

def require_manager_or_hr_or_admin():
    return require_role(["manager", "hr", "admin"])

def require_authenticated():
    return require_role(["employee", "manager", "hr", "admin"])