"""
User profile endpoint - update profile, change password
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.user import User
from app.schemas.auth import UserResponse
from app.schemas.profile import ProfileUpdate, PasswordChange, ProfileResponse
from app.services.auth_service import get_password_hash, verify_password
from app.dependencies import get_current_user
from app.middleware.rate_limiter import limiter
import logging

logger = logging.getLogger(__name__)

from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File
...
import os
import shutil

router = APIRouter(prefix="/api/profile", tags=["profile"])

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload a document for analysis"""
    try:
        docs_dir = os.path.abspath("documents")
        if not os.path.exists(docs_dir):
            os.makedirs(docs_dir)
            
        file_path = os.path.join(docs_dir, file.filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        logger.info(f"File uploaded: {file.filename} by user {current_user.id}")
        return {"success": True, "filename": file.filename, "message": "File ready for analysis"}
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/me", response_model=ProfileResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile with stats"""
    return ProfileResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        created_at=current_user.created_at,
        is_active=current_user.is_active,
    )


@router.put("/me", response_model=UserResponse)
def update_profile(
    profile_data: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update user profile (name only)"""
    # Check if email is being changed and if it's already taken
    if profile_data.email and profile_data.email != current_user.email:
        existing = db.query(User).filter(User.email == profile_data.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already taken"
            )
        current_user.email = profile_data.email

    if profile_data.full_name:
        current_user.full_name = profile_data.full_name

    if profile_data.phone_number:
        current_user.phone_number = profile_data.phone_number

    db.commit()
    db.refresh(current_user)

    logger.info(f"Profile updated for user {current_user.id}")
    return UserResponse.model_validate(current_user)


@router.post("/change-password")
@limiter.limit("3/minute")
def change_password(
    request: Request,
    password_data: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Change user password"""
    # Verify current password
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    # Check new password length
    if len(password_data.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 8 characters"
        )

    # Update password
    current_user.hashed_password = get_password_hash(password_data.new_password)
    db.commit()

    logger.info(f"Password changed for user {current_user.id}")
    return {"message": "Password changed successfully"}
