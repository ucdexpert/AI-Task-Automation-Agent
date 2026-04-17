from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional
import uuid
import logging
from datetime import datetime, timezone

from app.models.database import get_db, SessionLocal
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskResponse, TaskListResponse
from app.agents.orchestrator import MultiAgentOrchestrator
from app.dependencies import get_current_user_optional, get_current_user
from app.models.user import User
from app.services.email_service import send_task_completion_email
from app.services.websocket_service import manager
from app.utils.exceptions import NotFoundException

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

async def run_task_background(task_id: int, session_id: str, current_user_id: Optional[int]):
    """Background worker for processing tasks"""
    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return

        orchestrator = MultiAgentOrchestrator(db)
        result = await orchestrator.process_task(task, session_id)

        task.status = "completed" if result["success"] else "failed"
        task.result = result.get("result")
        task.tools_used = result.get("tools_used", [])
        task.error_message = result.get("error")
        task.completed_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(task)

        await manager.send_personal_message({
            "type": "task_complete",
            "task_id": task.id,
            "status": task.status,
            "result": task.result
        }, session_id)

        if current_user_id:
            user = db.query(User).filter(User.id == current_user_id).first()
            if user and user.email:
                try:
                    send_task_completion_email(
                        to_email=user.email,
                        user_name=user.full_name or "User",
                        task_description=task.user_input,
                        status=task.status,
                        task_id=task.id
                    )
                except Exception as e:
                    logger.error(f"Failed to send email notification: {e}")
    except Exception as e:
        logger.error(f"Error in background task: {e}")
        db.rollback()
        try:
            task = db.query(Task).filter(Task.id == task_id).first()
            if task:
                task.status = "failed"
                task.error_message = str(e)
                db.commit()
        except Exception: pass
    finally:
        db.close()

@router.post("/execute", response_model=TaskResponse)
async def execute_task(
    task_data: TaskCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session_id = task_data.session_id or str(uuid.uuid4())
    task = Task(
        user_input=task_data.user_input,
        status="processing",
        user_id=current_user.id,
        session_id=session_id
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    background_tasks.add_task(run_task_background, task.id, session_id, current_user.id)
    return TaskResponse.model_validate(task)

@router.get("/", response_model=TaskListResponse)
def list_tasks(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    query = db.query(Task)
    if current_user:
        query = query.filter(Task.user_id == current_user.id)

    tasks = query.order_by(Task.created_at.desc()).offset(skip).limit(limit).all()
    total = query.count()

    return TaskListResponse(
        tasks=[TaskResponse.model_validate(t) for t in tasks],
        total=total
    )

@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    query = db.query(Task).filter(Task.id == task_id)
    if current_user:
        query = query.filter(Task.user_id == current_user.id)

    task = query.first()
    if not task:
        raise NotFoundException("Task not found")

    return TaskResponse.model_validate(task)

@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not task:
        raise NotFoundException("Task not found")

    db.delete(task)
    db.commit()
    return {"message": "Task deleted successfully", "success": True}
