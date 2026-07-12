import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "RetainAI Backend API"
    VERSION: str = "1.0.0"
    DATABASE_URL: str = "sqlite:///database/retail.db"
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()
