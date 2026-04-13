from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from app.api.router import api_router
from app.config import settings
from app.models.database import engine, init_db
from app.models.user import User  # Import to register with Base
from app.models.task import Task, Conversation, AgentLog  # Import to register with Base
from app.utils.validators import validate_environment
from app.middleware.rate_limiter import limiter
from app.services.scheduler import start_scheduler, stop_scheduler
import logging

# Custom rate limit exceeded handler
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Please try again later."},
    )

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Validate environment on startup
validate_environment()

# Create database tables
init_db()
logger.info(f"✅ {settings.APP_NAME} v{settings.APP_VERSION} starting...")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.DEBUG else None,  # Disable docs in production
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Rate limiter setup
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# CORS middleware - restrict origins in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS if not settings.DEBUG else ["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    max_age=600,  # Cache preflight requests for 10 minutes
)

# Security: Trust only configured hosts
if not settings.DEBUG:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*.railway.app", "*.vercel.app", "localhost", "127.0.0.1"],
    )

# Include API routes
app.include_router(api_router)

@app.get("/")
def root():
    return {
        "message": "AI Task Automation Agent API",
        "version": settings.APP_VERSION,
        "docs": "/docs" if settings.DEBUG else "Disabled in production",
        "status": "running"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "debug": settings.DEBUG
    }

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Application startup complete")
    # Start background scheduler
    start_scheduler()

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("👋 Application shutting down")
    # Stop background scheduler
    stop_scheduler()
