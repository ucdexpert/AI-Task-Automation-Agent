import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from google.oauth2 import service_account
from googleapiclient.discovery import build
from app.tools.base import BaseTool
from app.config import settings

class GoogleCalendarTool(BaseTool):
    name = "google_calendar"
    description = "Manage Google Calendar events. Can create, list, and delete events. Use this to schedule meetings or check availability."
    
    def __init__(self):
        self.scopes = ['https://www.googleapis.com/auth/calendar']
        self._service = None

    def _get_service(self):
        if self._service:
            return self._service

        creds_dict = None
        
        # Try to load from file first (recommended)
        if settings.GOOGLE_CALENDAR_CREDENTIALS_FILE:
            try:
                with open(settings.GOOGLE_CALENDAR_CREDENTIALS_FILE, 'r') as f:
                    import json
                    creds_dict = json.load(f)
            except Exception as e:
                raise ValueError(f"Failed to load credentials file: {str(e)}")
        
        # Fallback to .env string
        if not creds_dict and settings.GOOGLE_CALENDAR_CREDENTIALS:
            try:
                import json
                creds_dict = json.loads(settings.GOOGLE_CALENDAR_CREDENTIALS)
            except Exception as e:
                raise ValueError(f"Failed to parse credentials from .env: {str(e)}")

        if not creds_dict:
            raise ValueError("Google Calendar credentials not configured. Please set GOOGLE_CALENDAR_CREDENTIALS_FILE or GOOGLE_CALENDAR_CREDENTIALS in .env")

        try:
            creds = service_account.Credentials.from_service_account_info(
                creds_dict, scopes=self.scopes
            )
            self._service = build('calendar', 'v3', credentials=creds)
            return self._service
        except Exception as e:
            raise Exception(f"Failed to initialize Google Calendar service: {str(e)}")

    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "operation": {
                "type": "string",
                "description": "Operation to perform: 'create', 'list', 'delete', 'update'",
                "enum": ["create", "list", "delete", "update"]
            },
            "summary": {
                "type": "string",
                "description": "Event title/summary"
            },
            "description": {
                "type": "string",
                "description": "Event description"
            },
            "start_time": {
                "type": "string",
                "description": "Start time in ISO format (e.g., '2023-12-31T10:00:00Z')"
            },
            "end_time": {
                "type": "string",
                "description": "End time in ISO format"
            },
            "event_id": {
                "type": "string",
                "description": "ID of the event (required for delete/update)"
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of events to list (default: 10)",
                "default": 10
            }
        }
    
    def get_required_parameters(self) -> list:
        return ["operation"]
    
    async def execute(self, operation: str, **kwargs) -> Dict[str, Any]:
        try:
            service = self._get_service()
            
            if operation == "create":
                return await self._create_event(service, kwargs)
            elif operation == "list":
                return await self._list_events(service, kwargs)
            elif operation == "delete":
                return await self._delete_event(service, kwargs)
            elif operation == "update":
                return await self._update_event(service, kwargs)
            else:
                return {"success": False, "message": f"Unsupported operation: {operation}"}
                
        except Exception as e:
            return {"success": False, "message": f"Calendar operation failed: {str(e)}"}

    async def _create_event(self, service, data: Dict[str, Any]) -> Dict[str, Any]:
        summary = data.get("summary", "New Event")
        start = data.get("start_time")
        end = data.get("end_time")
        
        if not start:
            # Default to now
            start = datetime.utcnow().isoformat() + 'Z'
        if not end:
            # Default to 1 hour later
            start_dt = datetime.fromisoformat(start.replace('Z', ''))
            end = (start_dt + timedelta(hours=1)).isoformat() + 'Z'
            
        event = {
            'summary': summary,
            'description': data.get("description", ""),
            'start': {'dateTime': start, 'timeZone': 'UTC'},
            'end': {'dateTime': end, 'timeZone': 'UTC'},
        }
        
        event = service.events().insert(calendarId='primary', body=event).execute()
        return {
            "success": True, 
            "message": "Event created successfully", 
            "event_id": event.get('id'),
            "htmlLink": event.get('htmlLink')
        }

    async def _list_events(self, service, data: Dict[str, Any]) -> Dict[str, Any]:
        max_results = data.get("max_results", 10)
        now = datetime.utcnow().isoformat() + 'Z'
        
        events_result = service.events().list(
            calendarId='primary', timeMin=now,
            maxResults=max_results, singleEvents=True,
            orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])
        
        formatted_events = []
        for e in events:
            formatted_events.append({
                "id": e.get('id'),
                "summary": e.get('summary'),
                "start": e.get('start', {}).get('dateTime') or e.get('start', {}).get('date'),
                "end": e.get('end', {}).get('dateTime') or e.get('end', {}).get('date'),
                "link": e.get('htmlLink')
            })
            
        return {"success": True, "events": formatted_events}

    async def _delete_event(self, service, data: Dict[str, Any]) -> Dict[str, Any]:
        event_id = data.get("event_id")
        if not event_id:
            return {"success": False, "message": "event_id is required for deletion"}
            
        service.events().delete(calendarId='primary', eventId=event_id).execute()
        return {"success": True, "message": f"Event {event_id} deleted successfully"}

    async def _update_event(self, service, data: Dict[str, Any]) -> Dict[str, Any]:
        event_id = data.get("event_id")
        if not event_id:
            return {"success": False, "message": "event_id is required for update"}
            
        # First get the event
        event = service.events().get(calendarId='primary', eventId=event_id).execute()
        
        # Update fields if provided
        if "summary" in data: event['summary'] = data['summary']
        if "description" in data: event['description'] = data['description']
        if "start_time" in data: event['start']['dateTime'] = data['start_time']
        if "end_time" in data: event['end']['dateTime'] = data['end_time']
        
        updated_event = service.events().update(calendarId='primary', eventId=event_id, body=event).execute()
        return {"success": True, "message": "Event updated successfully", "event_id": updated_event.get('id')}
