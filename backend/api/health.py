from fastapi import APIRouter
from backend.config.settings import settings

router = APIRouter()

@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "RetainAI Backend",
        "version": settings.VERSION
    }
