from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from app.models.database import get_db
from app.models.task import Task, AgentLog
from app.schemas.response import AnalyticsResponse, AgentLogResponse
from app.dependencies import get_current_user_optional
from app.models.user import User
from typing import List
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/dashboard", response_model=AnalyticsResponse)
def get_analytics(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Get dashboard analytics (filtered by user if authenticated)
    """
    query = db.query(Task)

    # Filter by user if authenticated
    if current_user:
        query = query.filter(Task.user_id == current_user.id)

    total_tasks = query.count()
    completed_tasks = query.filter(Task.status == "completed").count()
    failed_tasks = query.filter(Task.status == "failed").count()

    success_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

    # Average execution time from logs
    avg_time_result = db.query(func.avg(AgentLog.execution_time_ms)).first()
    avg_execution_time = float(avg_time_result[0]) if avg_time_result[0] else None

    # Most used tools
    tools_result = db.query(AgentLog.action, func.count(AgentLog.id)).group_by(AgentLog.action).all()
    most_used_tools = [{"tool": tool, "count": count} for tool, count in tools_result]
    most_used_tools.sort(key=lambda x: x["count"], reverse=True)

    # Tasks by date (last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    tasks_by_date_result = (
        db.query(func.date(Task.created_at), func.count(Task.id))
        .filter(Task.created_at >= seven_days_ago)
        .group_by(func.date(Task.created_at))
        .all()
    )
    tasks_by_date = [{"date": str(date), "count": count} for date, count in tasks_by_date_result]
    
    return AnalyticsResponse(
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        failed_tasks=failed_tasks,
        success_rate=round(success_rate, 2),
        avg_execution_time_ms=round(avg_execution_time, 2) if avg_execution_time else None,
        most_used_tools=most_used_tools[:10],
        tasks_by_date=tasks_by_date
    )

@router.get("/logs", response_model=List[AgentLogResponse])
def get_logs(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get agent execution logs
    """
    logs = (
        db.query(AgentLog)
        .order_by(AgentLog.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    return [AgentLogResponse.model_validate(log) for log in logs]

@router.get("/logs/{task_id}", response_model=List[AgentLogResponse])
def get_task_logs(task_id: int, db: Session = Depends(get_db)):
    """
    Get logs for a specific task
    """
    logs = (
        db.query(AgentLog)
        .filter(AgentLog.task_id == task_id)
        .order_by(AgentLog.step_number)
        .all()
    )
    
    return [AgentLogResponse.model_validate(log) for log in logs]
