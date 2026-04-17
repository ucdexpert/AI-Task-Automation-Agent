"""Tests for authentication service"""
import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from app.services import auth_service
from app.models.user import User


class TestPasswordHashing:
    """Test password hashing and verification"""

    def test_password_hashing(self):
        """Test that password is hashed correctly"""
        password = "TestPassword123!"
        hashed = auth_service.get_password_hash(password)

        # Hash should be a string
        assert isinstance(hashed, str)
        # Hash should be different from original password
        assert hashed != password
        # Hash should start with $2b$ (bcrypt format)
        assert hashed.startswith("$2b$")

    def test_password_verification_success(self):
        """Test correct password verification"""
        password = "TestPassword123!"
        hashed = auth_service.get_password_hash(password)

        assert auth_service.verify_password(password, hashed) is True

    def test_password_verification_failure(self):
        """Test incorrect password verification"""
        password = "TestPassword123!"
        hashed = auth_service.get_password_hash(password)

        assert auth_service.verify_password("WrongPassword", hashed) is False

    def test_different_hashes_for_same_password(self):
        """Test that same password generates different hashes (due to salt)"""
        password = "TestPassword123!"
        hash1 = auth_service.get_password_hash(password)
        hash2 = auth_service.get_password_hash(password)

        # Hashes should be different
        assert hash1 != hash2
        # But both should verify
        assert auth_service.verify_password(password, hash1)
        assert auth_service.verify_password(password, hash2)


class TestAccessToken:
    """Test JWT token creation and validation"""

    def test_create_access_token(self):
        """Test basic token creation"""
        data = {"sub": "user123"}
        token = auth_service.create_access_token(data)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_decode_access_token(self):
        """Test token can be decoded"""
        data = {"sub": "user123"}
        token = auth_service.create_access_token(data)

        payload = auth_service.decode_access_token(token)

        assert payload is not None
        assert payload["sub"] == "user123"

    def test_token_expiration_default(self):
        """Test token has correct expiration time"""
        data = {"sub": "user123"}
        token = auth_service.create_access_token(data)

        payload = auth_service.decode_access_token(token)

        assert "exp" in payload
        # Check expiration is approximately 24 hours from now (default)
        exp_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        now = datetime.now(timezone.utc)
        delta = exp_time - now
        assert delta.total_seconds() > 86000  # ~24 hours (allow some margin)
        assert delta.total_seconds() < 87000

    def test_token_expiration_custom(self):
        """Test custom expiration time"""
        data = {"sub": "user123"}
        expires_delta = timedelta(hours=1)
        token = auth_service.create_access_token(data, expires_delta=expires_delta)

        payload = auth_service.decode_access_token(token)

        exp_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        now = datetime.now(timezone.utc)
        delta = exp_time - now
        assert delta.total_seconds() > 3500  # ~1 hour
        assert delta.total_seconds() < 3700

    def test_token_with_extra_data(self):
        """Test token with additional claims"""
        data = {
            "sub": "user123",
            "email": "test@example.com",
            "role": "admin"
        }
        token = auth_service.create_access_token(data)

        payload = auth_service.decode_access_token(token)

        assert payload["sub"] == "user123"
        assert payload["email"] == "test@example.com"
        assert payload["role"] == "admin"

    def test_decode_invalid_token(self):
        """Test decoding invalid token returns None"""
        invalid_token = "invalid.token.here"

        payload = auth_service.decode_access_token(invalid_token)

        assert payload is None

    def test_decode_empty_token(self):
        """Test decoding empty string returns None"""
        payload = auth_service.decode_access_token("")
        assert payload is None

    def test_token_sub_converted_to_string(self):
        """Test that 'sub' is converted to string (jose requirement)"""
        data = {"sub": 12345}  # Integer sub
        token = auth_service.create_access_token(data)

        payload = auth_service.decode_access_token(token)

        assert isinstance(payload["sub"], str)
        assert payload["sub"] == "12345"

    def test_expired_token_rejection(self):
        """Test that expired tokens are rejected"""
        data = {"sub": "user123"}
        # Create token that expires immediately
        expires_delta = timedelta(seconds=-1)
        token = auth_service.create_access_token(data, expires_delta=expires_delta)

        payload = auth_service.decode_access_token(token)

        assert payload is None


class TestSecurityConcerns:
    """Test security-related configurations"""

    def test_jwt_secret_not_default(self):
        """CRITICAL: Test JWT secret is not using default value"""
        from app.config import settings

        # This test will fail if using default secret
        assert settings.JWT_SECRET != "super-secret-key-change-this", \
            "SECURITY RISK: JWT secret is using default value!"

    @patch('app.config.settings.JWT_SECRET', "super-secret-key-change-this")
    def test_warning_on_default_jwt_secret(self, caplog):
        """Test that using default JWT secret should raise warning"""
        # This documents the security issue
        data = {"sub": "user123"}
        token = auth_service.create_access_token(data)

        # Token can still be created (no prevention), but this is risky
        assert token is not None
        # In production, this should be prevented by validation
