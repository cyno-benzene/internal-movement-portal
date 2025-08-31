from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Convert minutes to seconds for timedelta
        expire_seconds = int(settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
        expire = datetime.utcnow() + timedelta(seconds=expire_seconds)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError as e:
        error_detail = "Could not validate credentials"
        if "expired" in str(e).lower():
            error_detail = "Token has expired. Please log in again."
        elif "invalid" in str(e).lower():
            error_detail = "Invalid token. Please log in again."
            
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_detail,
            headers={"WWW-Authenticate": "Bearer"},
        )
