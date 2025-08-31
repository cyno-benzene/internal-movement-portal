from fastapi import APIRouter, Depends
from app.api.v1.deps import get_current_user
from app.models.employee import Employee
from app.core.security import create_access_token
from app.schemas.auth import TokenResponse

router = APIRouter()

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(current_user: Employee = Depends(get_current_user)):
    """Refresh the access token for the current user"""
    access_token = create_access_token(data={
        "sub": str(current_user.id),
        "employee_id": current_user.employee_id,
        "role": current_user.role,
        "email": current_user.email,
        "name": current_user.name
    })
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=str(current_user.id),
        employee_id=current_user.employee_id,
        email=current_user.email,
        role=current_user.role,
        name=current_user.name
    )
