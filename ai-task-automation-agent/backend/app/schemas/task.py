from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class TaskCreate(BaseModel):
    user_input: str
    session_id: Optional[str] = None

class TaskResponse(BaseModel):
    id: int
    user_input: str
    status: str
    result: Optional[str] = None
    tools_used: Optional[List[str]] = None
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class TaskListResponse(BaseModel):
    tasks: List[TaskResponse]
    total: int
    
    model_config = ConfigDict(from_attributes=True)
