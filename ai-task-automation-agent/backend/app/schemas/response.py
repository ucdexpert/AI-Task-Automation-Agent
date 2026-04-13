from pydantic import BaseModel
from typing import Optional, List, Dict, Union
from datetime import datetime

class AnalyticsResponse(BaseModel):
    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    success_rate: float
    avg_execution_time_ms: Optional[float] = None
    most_used_tools: List[Dict[str, Union[str, int]]] = []
    tasks_by_date: List[Dict[str, Union[str, int]]] = []

class AgentLogResponse(BaseModel):
    id: int
    task_id: Optional[int] = None
    step_number: int
    action: str
    input_data: Optional[Dict] = None
    output_data: Optional[Dict] = None
    status: str
    execution_time_ms: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True
