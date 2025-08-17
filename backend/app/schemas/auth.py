from pydantic import BaseModel, EmailStr
from typing import Optional

class LoginRequest(BaseModel):
    employee_id: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    employee_id: str
    email: str
    role: str
    name: str

class UserCreate(BaseModel):
    employee_id: str
    email: EmailStr
    name: str
    password: str
    role: str = "employee"

class UserResponse(BaseModel):
    id: str
    employee_id: str
    email: str
    name: str
    role: str
    
    class Config:
        from_attributes = True