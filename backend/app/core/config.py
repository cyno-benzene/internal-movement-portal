from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://imp_user:imp_password@localhost:5432/imp_db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: float = 0.5  # 30 seconds for testing
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:4200", "*"]
    
    # App
    APP_NAME: str = "Internal Mobility Platform"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"

settings = Settings()
print(f"🔧 Settings loaded: ACCESS_TOKEN_EXPIRE_MINUTES = {settings.ACCESS_TOKEN_EXPIRE_MINUTES}")