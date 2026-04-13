from fastapi import APIRouter
from app.api.endpoints import tasks, conversations, analytics, auth, profile

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(tasks.router)
api_router.include_router(conversations.router)
api_router.include_router(analytics.router)
api_router.include_router(profile.router)
