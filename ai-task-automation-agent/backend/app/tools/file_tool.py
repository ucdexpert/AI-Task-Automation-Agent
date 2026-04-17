from app.tools.base import BaseTool
from typing import Any, Dict
import os
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class FileTool(BaseTool):
    name = "file_operations"
    description = "Read, analyze, and manage files including PDF, Excel, JSON, and Text. Can extract content for summarization."
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "operation": {
                "type": "string",
                "description": "Operation to perform: 'read_analyze', 'write', 'list'",
                "enum": ["read_analyze", "write", "list"]
            },
            "file_path": {
                "type": "string",
                "description": "Name or relative path of the file in documents folder."
            },
            "content": {
                "type": "string",
                "description": "Content to write (for write operation)."
            },
            "file_format": {
                "type": "string",
                "description": "File format: 'txt', 'json', 'md', 'pdf', 'xlsx'",
                "enum": ["txt", "json", "md", "pdf", "xlsx"]
            }
        }
    
    def get_required_parameters(self) -> list:
        return ["operation", "file_path"]
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        operation = kwargs.get("operation")
        file_path = kwargs.get("file_path")
        content = kwargs.get("content")
        file_format = kwargs.get("file_format", "txt")

        try:
            docs_dir = os.path.abspath("documents")
            if not os.path.exists(docs_dir): os.makedirs(docs_dir)
            
            target_path = os.path.abspath(os.path.join(docs_dir, file_path))
            if not target_path.startswith(docs_dir):
                return {"success": False, "message": "Security error: Restricted access."}
            
            if operation == "read_analyze":
                if not os.path.exists(target_path):
                    return {"success": False, "message": f"File {file_path} not found."}
                
                # --- PDF Analysis ---
                if target_path.endswith('.pdf'):
                    import PyPDF2
                    text = ""
                    with open(target_path, 'rb') as f:
                        reader = PyPDF2.PdfReader(f)
                        for page in reader.pages[:10]: # Read first 10 pages
                            text += page.extract_text() + "\n"
                    return {"success": True, "type": "pdf", "content": text[:8000]}

                # --- Excel Analysis ---
                elif target_path.endswith(('.xlsx', '.xls', '.csv')):
                    import pandas as pd
                    if target_path.endswith('.csv'):
                        df = pd.read_csv(target_path)
                    else:
                        df = pd.read_excel(target_path)
                    
                    summary = f"Columns: {list(df.columns)}\nRows: {len(df)}\nSample Data:\n{df.head(5).to_string()}"
                    return {"success": True, "type": "spreadsheet", "content": summary}

                # --- Text/JSON Analysis ---
                else:
                    with open(target_path, 'r', encoding='utf-8') as f:
                        data = f.read()
                    return {"success": True, "type": "text", "content": data[:8000]}

            elif operation == "write":
                with open(target_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return {"success": True, "message": f"File saved as {file_path}"}

            elif operation == "list":
                files = os.listdir(docs_dir)
                return {"success": True, "files": files}

            return {"success": False, "message": f"Unknown operation: {operation}"}
                
        except Exception as e:
            logger.error(f"File tool error: {e}")
            return {"success": False, "message": f"Error: {str(e)}"}
