from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from contextlib import asynccontextmanager

from app.api.router import api_router
from app.config import settings
from app.models.database import engine, init_db
from app.utils.validators import validate_environment
from app.middleware.rate_limiter import limiter
from app.services.scheduler import start_scheduler, stop_scheduler
from app.services.http_client import http_client
from app.utils.exceptions import (
    AppException, app_exception_handler, 
    global_exception_handler
)
import logging

# Configure logging based on environment
LOG_LEVEL = logging.INFO if settings.DEBUG else logging.WARNING
logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} starting...")
    validate_environment()
    init_db()
    await http_client.get_client() # Initialize global client
    start_scheduler()
    
    yield
    
    # Shutdown
    await http_client.close_client() # Close global client
    stop_scheduler()
    logger.info("👋 Application shut down complete")

# Custom rate limit handler
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Please try again later.", "success": False},
    )

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
)

# Exception Handlers
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# Rate limiter setup
app.state.limiter = limiter

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS if not settings.DEBUG else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=600,
)

if not settings.DEBUG:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*.railway.app", "*.vercel.app", "localhost", "127.0.0.1"],
    )

app.include_router(api_router)

@app.get("/")
def root():
    return {
        "message": "AI Task Automation Agent API",
        "status": "running"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}
