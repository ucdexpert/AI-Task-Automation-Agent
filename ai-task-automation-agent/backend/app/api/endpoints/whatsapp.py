from fastapi import APIRouter, Request, HTTPException, Depends, Query, Response
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.config import settings
from app.agents.orchestrator import MultiAgentOrchestrator
from app.models.task import Task
import logging
import json

# Prefix updated to match your Meta Dashboard /v1 convention
router = APIRouter(prefix="/api/v1/whatsapp", tags=["whatsapp"])
logger = logging.getLogger(__name__)

@router.get("/webhook")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge")
):
    """Verify the webhook with Meta (Returns PLAIN TEXT as required)"""
    logger.info(f"Verification attempt: mode={hub_mode}, token={hub_verify_token}")
    
    if hub_mode == "subscribe" and hub_verify_token == settings.WHATSAPP_VERIFY_TOKEN:
        logger.info("✅ Webhook verified successfully!")
        # IMPORTANT: Returning challenge as plain text response
        return Response(content=hub_challenge, media_type="text/plain")
    else:
        logger.warning("❌ Webhook verification failed! Token mismatch.")
        return Response(content="Verification failed", status_code=403)

@router.post("/webhook")
async def handle_whatsapp_message(request: Request, db: Session = Depends(get_db)):
    """Handle incoming WhatsApp messages and reply using AI Agent"""
    try:
        data = await request.json()
        logger.info(f"Incoming WhatsApp Data: {json.dumps(data)}")
        
        # Check if it's a valid WhatsApp message
        if "object" in data and data["object"] == "whatsapp_business_account":
            for entry in data.get("entry", []):
                for change in entry.get("changes", []):
                    value = change.get("value", {})
                    messages = value.get("messages", [])
                    
                    if messages:
                        message = messages[0]
                        sender_number = message.get("from")
                        message_body = message.get("text", {}).get("body")
                        
                        if message_body:
                            logger.info(f"Message from {sender_number}: {message_body}")
                            
                            # 1. Create a task record
                            new_task = Task(
                                user_input=message_body,
                                status="processing",
                                session_id=f"wa_{sender_number}"
                            )
                            db.add(new_task)
                            db.commit()
                            db.refresh(new_task)
                            
                            # 2. Trigger Orchestrator
                            # The system prompt will now tell the agent to reply via WhatsApp
                            orchestrator = MultiAgentOrchestrator(db)
                            await orchestrator.process_task(new_task, session_id=f"wa_{sender_number}")
                            
                            return Response(content="EVENT_RECEIVED", status_code=200)
                            
        return Response(content="IGNORED", status_code=200)
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return Response(content=str(e), status_code=500)
