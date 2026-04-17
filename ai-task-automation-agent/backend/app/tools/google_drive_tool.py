import os
import logging
from typing import Any, Dict, List
from google.oauth2 import service_account
from googleapiclient.discovery import build
from app.config import settings
from app.tools.base import BaseTool

logger = logging.getLogger(__name__)

class GoogleDriveTool(BaseTool):
    name = "google_drive"
    description = "Access and manage files on Google Drive. Can list files, search for specific documents, and read content."

    def __init__(self):
        self.scopes = ['https://www.googleapis.com/auth/drive.readonly']
        self.creds = None
        if os.path.exists(settings.GOOGLE_CALENDAR_CREDENTIALS_FILE):
            self.creds = service_account.Credentials.from_service_account_file(
                settings.GOOGLE_CALENDAR_CREDENTIALS_FILE, scopes=self.scopes)

    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "operation": {
                "type": "string",
                "description": "Operation to perform: 'list', 'search', 'read'",
                "enum": ["list", "search", "read"]
            },
            "query": {
                "type": "string",
                "description": "Search query or file name (for search/read operation)"
            },
            "file_id": {
                "type": "string",
                "description": "The specific Google Drive File ID (for read operation)"
            }
        }

    def get_required_parameters(self) -> list:
        return ["operation"]

    async def execute(self, **kwargs) -> Dict[str, Any]:
        if not self.creds:
            return {"success": False, "message": "Google Drive credentials not configured."}

        operation = kwargs.get("operation")
        query = kwargs.get("query")
        file_id = kwargs.get("file_id")

        try:
            service = build('drive', 'v3', credentials=self.creds)

            if operation == "list":
                results = service.files().list(
                    pageSize=10, fields="nextPageToken, files(id, name, mimeType)").execute()
                items = results.get('files', [])
                return {"success": True, "files": items}

            elif operation == "search":
                if not query: return {"success": False, "message": "Search requires a query."}
                results = service.files().list(
                    q=f"name contains '{query}'",
                    fields="files(id, name, mimeType)").execute()
                items = results.get('files', [])
                return {"success": True, "results": items}

            elif operation == "read":
                # If we have file_id, use it, otherwise search by name first
                target_id = file_id
                if not target_id and query:
                    search_res = service.files().list(q=f"name = '{query}'", fields="files(id)").execute()
                    files = search_res.get('files', [])
                    if not files: return {"success": False, "message": f"File '{query}' not found."}
                    target_id = files[0]['id']
                
                if not target_id: return {"success": False, "message": "File ID or Name required for read."}
                
                # Fetch metadata to check type
                file_meta = service.files().get(fileId=target_id, fields="name, mimeType").execute()
                
                # If it's a Google Doc, we need to export it as text
                if file_meta['mimeType'] == 'application/vnd.google-apps.document':
                    content = service.files().export(fileId=target_id, mimeType='text/plain').execute()
                    return {"success": True, "name": file_meta['name'], "content": content.decode('utf-8')[:8000]}
                else:
                    return {"success": False, "message": "Only Google Docs are currently supported for direct reading. Use 'list' for other files."}

            return {"success": False, "message": f"Unknown operation: {operation}"}

        except Exception as e:
            logger.error(f"Google Drive error: {e}")
            return {"success": False, "message": f"Drive Error: {str(e)}"}
