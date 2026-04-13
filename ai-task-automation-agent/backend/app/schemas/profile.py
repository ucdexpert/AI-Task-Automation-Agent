"""
Profile schemas for user profile management
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


class ProfileResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True
