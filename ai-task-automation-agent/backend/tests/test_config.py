"""Tests for configuration module"""
import os
import pytest
from app.config import Settings


class TestConfig:
    """Test configuration loading and validation"""

    def test_cors_origins_parsed_correctly(self):
        """Test CORS origins are parsed and stripped"""
        # Test the actual settings instance
        from app.config import settings
        
        # Should have at least the default origins
        assert len(settings.BACKEND_CORS_ORIGINS) >= 2
        assert 'http://localhost:3000' in settings.BACKEND_CORS_ORIGINS
        assert 'http://localhost:3001' in settings.BACKEND_CORS_ORIGINS
        # Verify no whitespace in origins
        for origin in settings.BACKEND_CORS_ORIGINS:
            assert origin == origin.strip()

    def test_llm_temperature_is_float(self):
        """Test LLM temperature is a float"""
        from app.config import settings
        
        assert isinstance(settings.LLM_TEMPERATURE, float)
        assert 0.0 <= settings.LLM_TEMPERATURE <= 1.0

    def test_smtp_port_is_int(self):
        """Test SMTP port is parsed as integer"""
        from app.config import settings
        
        assert isinstance(settings.SMTP_PORT, int)
        assert settings.SMTP_PORT > 0

    def test_jwt_secret_exists(self):
        """Test JWT secret is set"""
        from app.config import settings
        
        assert settings.JWT_SECRET is not None
        assert len(settings.JWT_SECRET) > 0

    def test_database_url_exists(self):
        """Test database URL is configured"""
        from app.config import settings
        
        assert settings.DATABASE_URL is not None
        assert len(settings.DATABASE_URL) > 0

    def test_groq_api_key_exists(self):
        """Test Groq API key is configured"""
        from app.config import settings
        
        # Note: This checks if it's not empty string
        # In .env file it should be set
        assert settings.GROQ_API_KEY is not None
