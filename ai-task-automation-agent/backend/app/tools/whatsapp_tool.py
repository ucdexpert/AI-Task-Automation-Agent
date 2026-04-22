"""WhatsApp notification tool using Meta Cloud API with Interactive Buttons support"""
from typing import Optional, Dict, Any
from app.config import settings
from app.tools.base import BaseTool
from app.services.http_client import http_client
import logging

logger = logging.getLogger(__name__)

class WhatsAppTool(BaseTool):
    name = "whatsapp"
    description = "Send WhatsApp messages via Meta Cloud API. Supports text and template messages."

    def __init__(self):
        self.base_url = f"https://graph.facebook.com/v18.0/{settings.WHATSAPP_PHONE_NUMBER_ID}"
        self.headers = {
            "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
            "Content-Type": "application/json",
        }

    async def execute(self, **kwargs) -> Dict[str, Any]:
        operation = kwargs.get("operation", "send_text")
        if operation == "send_text":
            return await self.send_text_message(kwargs.get("message"), kwargs.get("to_number"))
        elif operation == "send_template":
            return await self.send_template_message(
                template_name=kwargs.get("template_name"),
                to_number=kwargs.get("to_number"),
                language=kwargs.get("language", "en_US"),
                components=kwargs.get("components", [])
            )
        return {"success": False, "message": f"Unsupported operation: {operation}"}

    async def send_template_message(self, template_name: str, to_number: str, language: str = "en_US", components: list = []) -> Dict[str, Any]:
        """Send a pre-approved template message"""
        payload = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": language},
                "components": components
            }
        }
        return await self._send_request(payload)

    async def send_text_message(self, message: str, to_number: Optional[str] = None) -> Dict[str, Any]:
        recipient = to_number or settings.WHATSAPP_RECIPIENT_NUMBER
        if not recipient:
            return {"success": False, "message": "No recipient number provided"}

        payload = {
            "messaging_product": "whatsapp",
            "to": recipient,
            "type": "text",
            "text": {"body": message},
        }
        return await self._send_request(payload)

    async def _send_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        recipient = payload.get("to")
        try:
            client = await http_client.get_client()
            url = f"{self.base_url}/messages"
            
            logger.info(f"📤 Sending WhatsApp to {recipient} via {url}")
            
            response = await client.post(
                url,
                headers=self.headers,
                json=payload
            )
            
            if response.status_code in [200, 201]:
                logger.info("✅ WhatsApp message sent successfully!")
                return {"success": True, "message": "Message sent successfully", "data": response.json()}
            else:
                error_data = response.json()
                logger.error(f"❌ WhatsApp API Error ({response.status_code}): {error_data}")
                return {
                    "success": False, 
                    "message": f"Meta API Error {response.status_code}", 
                    "details": error_data.get("error", {}).get("message", "Unknown error")
                }
        except Exception as e:
            logger.error(f"❌ WhatsApp Tool Exception: {str(e)}")
            return {"success": False, "message": f"Internal Tool Error: {str(e)}"}
