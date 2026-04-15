from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional
from app.models.database import get_db, SessionLocal
from app.models.task import Task
from app.config import settings
from app.schemas.task import TaskCreate, TaskResponse, TaskListResponse
from app.agents.orchestrator import MultiAgentOrchestrator
from app.dependencies import get_current_user_optional, get_current_user
from app.models.user import User
from app.services.email_service import send_task_completion_email
from app.services.websocket_service import manager
import uuid
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

async def run_task_background(task_id: int, session_id: str, current_user_id: Optional[int]):
    """Background worker for processing tasks"""
    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return

        # Process task with agent
        orchestrator = MultiAgentOrchestrator(db)
        result = await orchestrator.process_task(task, session_id)

        # Update task record
        task.status = "completed" if result["success"] else "failed"
        task.result = result.get("result")
        task.tools_used = result.get("tools_used", [])
        task.error_message = result.get("error")
        task.completed_at = datetime.utcnow()
        db.commit()
        db.refresh(task)

        # Send final WebSocket update
        await manager.send_personal_message({
            "type": "task_complete",
            "task_id": task.id,
            "status": task.status,
            "result": task.result
        }, session_id)

        # Send email notification
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
        # Rollback the failed transaction first!
        db.rollback()
        # Update task status to failed so frontend stops polling
        try:
            task = db.query(Task).filter(Task.id == task_id).first()
            if task:
                task.status = "failed"
                task.error_message = str(e)
                db.commit()
        except Exception as db_err:
            logger.error(f"Failed to update task status on error: {db_err}")
    finally:
        db.close()


@router.post("/execute", response_model=TaskResponse)
async def execute_task(
    task_data: TaskCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Execute a new task using the AI agent (Background Mode)
    """
    # Create session ID if not provided
    session_id = task_data.session_id or str(uuid.uuid4())

    # Create task record
    task = Task(
        user_input=task_data.user_input,
        status="processing",
        user_id=current_user.id if current_user else None,
        session_id=session_id
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    # Start task in background
    background_tasks.add_task(
        run_task_background, 
        task.id, 
        session_id, 
        current_user.id if current_user else None
    )

    return TaskResponse.from_orm(task)


@router.get("/", response_model=TaskListResponse)
def list_tasks(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    List tasks (filtered by user if authenticated)
    """
    query = db.query(Task)

    # Filter by user if authenticated
    if current_user:
        query = query.filter(Task.user_id == current_user.id)

    tasks = query.order_by(Task.created_at.desc()).offset(skip).limit(limit).all()
    total = query.count()

    return TaskListResponse(
        tasks=[TaskResponse.from_orm(t) for t in tasks],
        total=total
    )


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Get a specific task (only if user owns it)
    """
    query = db.query(Task).filter(Task.id == task_id)

    # Filter by user if authenticated
    if current_user:
        query = query.filter(Task.user_id == current_user.id)

    task = query.first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return TaskResponse.from_orm(task)


@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a task (only if user owns it)
    """
    task = (
        db.query(Task)
        .filter(Task.id == task_id, Task.user_id == current_user.id)
        .first()
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()
    return {"message": "Task deleted successfully"}
