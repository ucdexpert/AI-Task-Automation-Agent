from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import api_router
from app.config import settings
from app.models.database import engine, init_db
from app.models.user import User  # Import to register with Base
from app.models.task import Task, Conversation, AgentLog  # Import to register with Base

# Create database tables
init_db()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router)

@app.get("/")
def root():
    return {
        "message": "AI Task Automation Agent API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}
