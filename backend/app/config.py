import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "SkillAlpha API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # Security
    JWT_SECRET: str = os.getenv("JWT_SECRET", "skillalpha_super_secret_jwt_key_production_2026_change_me")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./skillalpha.db")
    
    # LLM Integration (Groq / OpenAI)
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", os.getenv("LLM_API_KEY", ""))
    LLM_MODEL: str = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    
    class Config:
        case_sensitive = True

settings = Settings()
