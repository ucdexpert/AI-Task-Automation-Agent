"""WhatsApp notification tool using Meta Cloud API with Interactive Buttons support"""
import httpx
from typing import Optional, Dict, Any, List
from app.config import settings
from app.tools.base import BaseTool
import logging

logger = logging.getLogger(__name__)

class WhatsAppTool(BaseTool):
    name = "whatsapp"
    description = "Send WhatsApp messages, templates, and interactive buttons to users"
    
    def __init__(self):
        self.base_url = "https://graph.facebook.com/v18.0"
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "operation": {
                "type": "string",
                "enum": ["send_text", "send_template", "send_buttons"],
                "description": "Type of WhatsApp message to send"
            },
            "message": {
                "type": "string",
                "description": "Text message content"
            },
            "template_name": {
                "type": "string",
                "description": "Template name"
            },
            "buttons": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of button titles (max 3 for Quick Replies)"
            },
            "to_number": {
                "type": "string",
                "description": "Recipient phone number"
            }
        }
    
    def get_required_parameters(self) -> list:
        return ["operation"]

    async def execute(self, **kwargs) -> Dict[str, Any]:
        operation = kwargs.get("operation")
        logger.info(f"WhatsApp tool executing operation: {operation} with args: {kwargs}")
        
        if operation == "send_text":
            return await self.send_text_message(
                message=kwargs.get("message", ""),
                to_number=kwargs.get("to_number")
            )
        elif operation == "send_template":
            return await self.send_template_message(
                template_name=kwargs.get("template_name", "hello_world"),
                to_number=kwargs.get("to_number")
            )
        elif operation == "send_buttons":
            return await self.send_interactive_buttons(
                message=kwargs.get("message", "Please choose an option:"),
                buttons=kwargs.get("buttons", ["Yes", "No"]),
                to_number=kwargs.get("to_number")
            )
        else:
            return {"success": False, "message": f"Unknown operation: {operation}"}
    
    async def send_text_message(self, message: str, to_number: Optional[str] = None) -> Dict[str, Any]:
        """Send a plain text message"""
        if not message:
            return {"success": False, "message": "Message content cannot be empty"}
            
        recipient = to_number or settings.WHATSAPP_RECIPIENT_NUMBER
        return await self._send_payload({
            "messaging_product": "whatsapp",
            "to": recipient,
            "type": "text",
            "text": {"body": message}
        })

    async def send_interactive_buttons(self, message: str, buttons: List[str], to_number: Optional[str] = None) -> Dict[str, Any]:
        """Send a message with Quick Reply buttons (Max 3)"""
        recipient = to_number or settings.WHATSAPP_RECIPIENT_NUMBER
        
        button_objects = []
        for i, btn_text in enumerate(buttons[:3]):
            button_objects.append({
                "type": "reply",
                "reply": {
                    "id": f"btn_{i}",
                    "title": btn_text
                }
            })
            
        payload = {
            "messaging_product": "whatsapp",
            "to": recipient,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": message},
                "action": {"buttons": button_objects}
            }
        }
        return await self._send_payload(payload)

    async def send_template_message(self, template_name: str, to_number: Optional[str] = None) -> Dict[str, Any]:
        """Send a template message"""
        recipient = to_number or settings.WHATSAPP_RECIPIENT_NUMBER
        payload = {
            "messaging_product": "whatsapp",
            "to": recipient,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": "en_US"}
            }
        }
        return await self._send_payload(payload)

    async def _send_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Helper to send the request to Meta API with detailed error logging"""
        if not settings.WHATSAPP_PHONE_NUMBER_ID or not settings.WHATSAPP_ACCESS_TOKEN:
            return {"success": False, "message": "WhatsApp credentials not configured"}
        
        url = f"{self.base_url}/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
        headers = {
            "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        
        try:
            logger.info(f"Sending WhatsApp payload to {url}: {payload}")
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=payload)
                result = response.json()
            
            if response.status_code == 200:
                logger.info("WhatsApp message sent successfully!")
                return {"success": True, "message_id": result.get("messages", [{}])[0].get("id")}
            else:
                error_msg = result.get("error", {}).get("message", "Unknown error")
                logger.error(f"WhatsApp API Error (Status {response.status_code}): {error_msg}")
                logger.error(f"Full Error Response: {result}")
                return {
                    "success": False, 
                    "status_code": response.status_code,
                    "error_type": result.get("error", {}).get("type"),
                    "message": error_msg,
                    "full_error": result
                }
        except Exception as e:
            logger.error(f"WhatsApp Exception: {str(e)}")
            return {"success": False, "message": str(e)}
