"""Tests for API endpoints - Tasks"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from httpx import AsyncClient


class TestTaskEndpoints:
    """Test task API endpoints"""

    @pytest.mark.asyncio
    @patch('app.agents.orchestrator.MultiAgentOrchestrator.process_task')
    async def test_execute_task_success(self, mock_process, client, auth_headers):
        """Test successful task execution (POST /api/tasks/execute)"""
        mock_process.return_value = {
            "success": True,
            "result": "Task completed",
            "tools_used": [],
            "steps": 1,
            "execution_time_ms": 100,
            "logs": []
        }
        
        task_data = {
            "user_input": "Hello agent",
            "session_id": "test_session"
        }

        response = await client.post("/api/tasks/execute", json=task_data, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["user_input"] == "Hello agent"
        assert data["status"] in ["completed", "processing"]

    @pytest.mark.asyncio
    async def test_execute_task_unauthorized(self, client):
        """Test task execution without authentication"""
        task_data = {
            "user_input": "Hello agent"
        }
        response = await client.post("/api/tasks/execute", json=task_data)
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_task_by_id(self, client, auth_headers, db_session):
        """Test getting a task by ID"""
        from app.models.task import Task

        # Create a test task
        task = Task(
            user_input="Test Task",
            status="pending",
            user_id=1
        )
        db_session.add(task)
        db_session.commit()

        response = await client.get(f"/api/tasks/{task.id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task.id
        assert data["user_input"] == "Test Task"

    @pytest.mark.asyncio
    async def test_list_tasks(self, client, auth_headers, db_session):
        """Test listing user's tasks"""
        from app.models.task import Task

        # Create multiple tasks
        for i in range(5):
            task = Task(
                user_input=f"Task {i}",
                status="completed",
                user_id=1
            )
            db_session.add(task)
        db_session.commit()

        response = await client.get("/api/tasks/", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "tasks" in data
        assert isinstance(data["tasks"], list)
        assert data["total"] >= 5

    @pytest.mark.asyncio
    async def test_delete_task(self, client, auth_headers, db_session):
        """Test deleting a task"""
        from app.models.task import Task

        task = Task(
            user_input="Delete me",
            status="pending",
            user_id=1
        )
        db_session.add(task)
        db_session.commit()

        response = await client.delete(f"/api/tasks/{task.id}", headers=auth_headers)
        assert response.status_code == 200

        # Verify task is deleted
        response = await client.get(f"/api/tasks/{task.id}", headers=auth_headers)
        assert response.status_code == 404
