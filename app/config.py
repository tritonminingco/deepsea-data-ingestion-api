import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost/deepsea_db"
    
    # Redis for caching and WebSocket
    REDIS_URL: str = "redis://localhost:6379"
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "DeepSea Data Ingestion API"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # WebSocket
    WS_MESSAGE_QUEUE_URL: str = "redis://localhost:6379"
    
    # ISA Compliance Settings
    ISA_ZONE_TIMEOUT_MINUTES: int = 30
    ISA_REPORTING_INTERVAL_HOURS: int = 24
    
    class Config:
        env_file = ".env"


settings = Settings()
