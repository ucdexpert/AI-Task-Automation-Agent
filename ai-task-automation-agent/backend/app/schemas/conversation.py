from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime

class ConversationCreate(BaseModel):
    session_id: str
    role: str  # user or assistant
    message: str
    extra_data: Optional[Dict] = None

class ConversationResponse(BaseModel):
    id: int
    session_id: str
    role: str
    message: str
    extra_data: Optional[Dict] = None
    created_at: datetime

    class Config:
        from_attributes = True
