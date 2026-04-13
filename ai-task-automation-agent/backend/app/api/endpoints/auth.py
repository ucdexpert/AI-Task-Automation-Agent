from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from app.models.database import get_db
from app.models.user import User
from app.schemas.auth import UserCreate, UserLogin, UserResponse, TokenResponse
from app.services.auth_service import get_password_hash, verify_password, create_access_token
from app.dependencies import get_current_user
from app.middleware.rate_limiter import limiter
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
@limiter.limit("3/minute")
def register(request: Request, user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Create new user
        user = User(
            email=user_data.email,
            hashed_password=get_password_hash(user_data.password),
            full_name=user_data.full_name
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # Create token
        access_token = create_access_token(data={"sub": user.id})

        return TokenResponse(
            access_token=access_token,
            user=UserResponse.from_orm(user)
        )
    except OperationalError as e:
        logger.error(f"Database operational error during register: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error. Please try again."
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during register: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
def login(request: Request, user_data: UserLogin, db: Session = Depends(get_db)):
    """Login user"""
    try:
        user = db.query(User).filter(User.email == user_data.email).first()
        if not user or not verify_password(user_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is deactivated"
            )

        access_token = create_access_token(data={"sub": user.id})

        return TokenResponse(
            access_token=access_token,
            user=UserResponse.from_orm(user)
        )
    except OperationalError as e:
        logger.error(f"Database operational error during login: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error. Please try again."
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during login: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Get current user info"""
    return UserResponse.from_orm(current_user)
