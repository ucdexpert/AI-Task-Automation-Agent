from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app.models.database import get_db
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskResponse, TaskListResponse
from app.agents.orchestrator import AgentOrchestrator
from app.dependencies import get_current_user_optional, get_current_user
from app.models.user import User
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.post("/execute", response_model=TaskResponse)
async def execute_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Execute a new task using the AI agent
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

    # Process task with agent
    orchestrator = AgentOrchestrator(db)
    result = await orchestrator.process_task(task, session_id)

    # Update task record
    task.status = "completed" if result["success"] else "failed"
    task.result = result.get("result")
    task.tools_used = result.get("tools_used", [])
    task.error_message = result.get("error")
    task.completed_at = datetime.utcnow()
    db.commit()
    db.refresh(task)

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
