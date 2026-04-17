"""Tests for API endpoints - Authentication"""
import pytest
from unittest.mock import patch, MagicMock
from httpx import AsyncClient


class TestAuthEndpoints:
    """Test authentication API endpoints"""

    @pytest.mark.asyncio
    async def test_register_success(self, client, db_session):
        """Test successful user registration"""
        user_data = {
            "email": "newuser@example.com",
            "password": "SecurePass123!",
            "full_name": "New User"
        }

        response = await client.post("/api/auth/register", json=user_data)

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["email"] == "newuser@example.com"
        assert "password" not in data["user"]

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client, db_session, test_user_data):
        """Test registration with duplicate email"""
        # First registration
        await client.post("/api/auth/register", json=test_user_data)

        # Second registration with same email
        response = await client.post("/api/auth/register", json=test_user_data)

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_register_invalid_email(self, client):
        """Test registration with invalid email"""
        user_data = {
            "email": "invalid-email",
            "password": "SecurePass123!",
            "full_name": "Test User"
        }

        response = await client.post("/api/auth/register", json=user_data)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_login_success(self, client, db_session, test_user_data):
        """Test successful login"""
        # Register user first
        await client.post("/api/auth/register", json=test_user_data)

        # Login
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }

        response = await client.post("/api/auth/login", json=login_data)

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["email"] == test_user_data["email"]

    @pytest.mark.asyncio
    async def test_get_current_user(self, client, auth_headers):
        """Test getting current user profile"""
        response = await client.get("/api/auth/me", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "email" in data
        assert "id" in data

    @pytest.mark.asyncio
    async def test_get_current_user_unauthorized(self, client):
        """Test getting current user without auth"""
        response = await client.get("/api/auth/me")
        assert response.status_code == 401
