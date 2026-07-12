import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from backend.config.settings import settings
from backend.utils.logger import logger
from backend.api.health import router as health_router
from backend.api.dashboard import router as dashboard_router

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
app.include_router(dashboard_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=settings.API_HOST, port=settings.API_PORT, reload=True)
