import os

files = {
    "backend/__init__.py": "",
    "backend/api/__init__.py": "",
    "backend/api/health.py": """from fastapi import APIRouter
from backend.config.settings import settings

router = APIRouter()

@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "RetainAI Backend",
        "version": settings.VERSION
    }
""",
    "backend/config/__init__.py": "",
    "backend/config/settings.py": """import os
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
""",
    "backend/database/__init__.py": "",
    "backend/database/connection.py": """import sqlite3
import logging
from backend.config.settings import settings

logger = logging.getLogger(__name__)

def get_db_connection():
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    try:
        conn = sqlite3.connect(db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        logger.error(f"Database connection error: {e}")
        raise e
        
def close_db_connection(conn):
    if conn:
        conn.close()
""",
    "backend/services/__init__.py": "",
    "backend/schemas/__init__.py": "",
    "backend/ml/__init__.py": "",
    "backend/utils/__init__.py": "",
    "backend/utils/logger.py": """import logging

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    return logging.getLogger("backend")

logger = setup_logging()
""",
    "backend/main.py": """import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from backend.config.settings import settings
from backend.utils.logger import logger
from backend.api.health import router as health_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend services for the RetainAI platform.",
    version=settings.VERSION
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow localhost development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": "Internal Server Error"}
    )

# Include routers
app.include_router(health_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=settings.API_HOST, port=settings.API_PORT, reload=True)
"""
}

for path, content in files.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

print("Backend files created successfully.")
