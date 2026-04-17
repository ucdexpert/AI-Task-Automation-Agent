"""Test configuration and fixtures for the backend API"""
import os
import pytest
from unittest.mock import MagicMock, patch
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.models.database import Base, get_db
from app.config import settings

# Test database (in-memory SQLite)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
async def client(db_session):
    """Create a test client with overridden dependencies"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    # Disable rate limiting for tests
    from app.middleware.rate_limiter import limiter
    limiter.enabled = False

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def mock_groq_client():
    """Mock Groq API client"""
    with patch('app.services.llm_service.Groq') as mock_groq:
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message = MagicMock()
        mock_response.choices[0].message.content = "Test response"
        mock_groq.return_value.chat.completions.create.return_value = mock_response
        yield mock_groq


@pytest.fixture
def mock_whatsapp_tool():
    """Mock WhatsAppTool to avoid actual API calls"""
    with patch('app.tools.whatsapp_tool.WhatsAppTool') as mock:
        mock_instance = MagicMock()
        mock_instance.execute.return_value = {
            "success": True,
            "message_id": "test_message_123",
            "recipient": "+923001234567"
        }
        mock.return_value = mock_instance
        yield mock


@pytest.fixture
def mock_google_calendar():
    """Mock Google Calendar API"""
    with patch('app.tools.google_calendar_tool.build') as mock_build:
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        yield mock_build


@pytest.fixture
def test_user_data():
    """Sample user data for tests"""
    return {
        "email": "test@example.com",
        "password": "TestPassword123!",
        "full_name": "Test User"
    }


@pytest.fixture
def auth_headers(client, test_user_data, db_session):
    """Create a test user and return auth headers"""
    from app.services.auth_service import get_password_hash, create_access_token
    from app.models.user import User

    # Create user directly in DB for testing
    user = User(
        email=test_user_data["email"],
        hashed_password=get_password_hash(test_user_data["password"]),
        full_name=test_user_data["full_name"]
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    token = create_access_token(data={"sub": user.id})

    return {"Authorization": f"Bearer {token}"}
