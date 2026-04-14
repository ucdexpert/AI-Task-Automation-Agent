"""Calendar notification tool - sends WhatsApp notifications for calendar events"""
from typing import Dict, Any, Optional
from app.config import settings
from app.tools.base import BaseTool
from app.tools.whatsapp_tool import WhatsAppTool


class CalendarNotificationTool(BaseTool):
    name = "calendar_notification"
    description = "Send WhatsApp notifications when calendar events are created or updated"
    
    def __init__(self):
        super().__init__()
        self.whatsapp_tool = WhatsAppTool()
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "event_summary": {
                "type": "string",
                "description": "Event title/summary"
            },
            "event_start": {
                "type": "string",
                "description": "Event start time"
            },
            "event_end": {
                "type": "string",
                "description": "Event end time"
            },
            "notification_type": {
                "type": "string",
                "enum": ["event_created", "event_reminder", "event_cancelled"],
                "description": "Type of notification"
            },
            "message": {
                "type": "string",
                "description": "Custom message (optional)"
            }
        }
    
    def get_required_parameters(self) -> list:
        return ["event_summary", "event_start", "notification_type"]
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        event_summary = kwargs.get("event_summary", "")
        event_start = kwargs.get("event_start", "")
        event_end = kwargs.get("event_end", "")
        notification_type = kwargs.get("notification_type", "event_created")
        custom_message = kwargs.get("message")
        
        # Build notification message
        if notification_type == "event_created":
            message = f"📅 New Event Created!\n\n"
            message += f"📌 {event_summary}\n"
            message += f"🕐 Start: {event_start}\n"
            if event_end:
                message += f" End: {event_end}\n"
            message += f"\n✅ Event added to your calendar"
        elif notification_type == "event_reminder":
            message = f"⏰ Event Reminder!\n\n"
            message += f"📌 {event_summary}\n"
            message += f"🕐 Starting at: {event_start}\n"
            message += f"\n🔔 Don't forget to attend!"
        elif notification_type == "event_cancelled":
            message = f"❌ Event Cancelled\n\n"
            message += f"📌 {event_summary}\n"
            message += f"🕐 Was scheduled for: {event_start}\n"
            message += f"\n⚠️ This event has been cancelled"
        else:
            message = f"📅 Calendar Update\n\n{event_summary}"
        
        # Use custom message if provided
        if custom_message:
            message = custom_message
        
        # Send via WhatsApp
        return await self.whatsapp_tool.send_text_message(message=message)
