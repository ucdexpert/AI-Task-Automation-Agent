from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.task import Conversation
from app.schemas.conversation import ConversationCreate, ConversationResponse
from typing import List

router = APIRouter(prefix="/api/conversations", tags=["conversations"])

@router.post("/", response_model=ConversationResponse)
def create_conversation(conv_data: ConversationCreate, db: Session = Depends(get_db)):
    """
    Create a new conversation message
    """
    conversation = Conversation(
        session_id=conv_data.session_id,
        role=conv_data.role,
        message=conv_data.message,
        extra_data=conv_data.extra_data
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    
    return ConversationResponse.model_validate(conversation)

@router.get("/{session_id}", response_model=List[ConversationResponse])
def get_conversation_history(
    session_id: str,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get conversation history for a session
    """
    conversations = (
        db.query(Conversation)
        .filter(Conversation.session_id == session_id)
        .order_by(Conversation.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    return [ConversationResponse.model_validate(c) for c in conversations]
