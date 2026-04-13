from sqlalchemy.orm import Session
from app.models.task import Conversation
from typing import List, Optional, Dict, Any

class AgentMemory:
    """
    Manages conversation history and task context
    """
    def __init__(self, db: Session):
        self.db = db
    
    def add_message(self, session_id: str, role: str, message: str, extra_data: Dict[str, Any] = None):
        """Add a message to conversation history"""
        conversation = Conversation(
            session_id=session_id,
            role=role,
            message=message,
            extra_data=extra_data
        )
        self.db.add(conversation)
        self.db.commit()
        return conversation
    
    def get_conversation_history(self, session_id: str, limit: int = 20) -> List[Conversation]:
        """Get recent conversation history for a session"""
        return (
            self.db.query(Conversation)
            .filter(Conversation.session_id == session_id)
            .order_by(Conversation.created_at.desc())
            .limit(limit)
            .all()
        )
    
    def get_context_messages(self, session_id: str) -> List[Dict[str, str]]:
        """Get formatted context messages for LLM"""
        history = self.get_conversation_history(session_id, limit=10)
        history.reverse()  # Reverse to get chronological order
        
        return [
            {"role": msg.role, "content": msg.message}
            for msg in history
        ]
    
    def clear_session(self, session_id: str):
        """Clear all messages for a session"""
        self.db.query(Conversation).filter(
            Conversation.session_id == session_id
        ).delete()
        self.db.commit()
