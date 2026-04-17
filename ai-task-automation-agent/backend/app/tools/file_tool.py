from app.tools.base import BaseTool
from typing import Any, Dict
import os
import json
from datetime import datetime

class FileTool(BaseTool):
    name = "file_operations"
    description = "Perform file operations including reading, writing, and managing documents. Can save reports, read files, and manage document storage."
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "operation": {
                "type": "string",
                "description": "Operation to perform: 'write', 'read', 'list'",
                "enum": ["write", "read", "list"]
            },
            "file_path": {
                "type": "string",
                "description": "Path to the file or directory"
            },
            "content": {
                "type": "string",
                "description": "Content to write to file (for write operation)"
            },
            "file_format": {
                "type": "string",
                "description": "File format: 'txt', 'json', 'md'",
                "enum": ["txt", "json", "md"]
            }
        }
    
    def get_required_parameters(self) -> list:
        return ["operation", "file_path"]
    
    async def execute(self, operation: str, file_path: str, content: str = None, file_format: str = "txt", **kwargs) -> Dict[str, Any]:
        """
        Perform file operations
        """
        try:
            # Create documents directory if it doesn't exist
            docs_dir = os.path.abspath("documents")
            if not os.path.exists(docs_dir):
                os.makedirs(docs_dir)
            
            # Security: Prevent path traversal
            target_path = os.path.abspath(os.path.join(docs_dir, file_path))
            if not target_path.startswith(docs_dir):
                return {
                    "success": False,
                    "message": "Security error: Path traversal attempt detected."
                }
            
            full_path = target_path
            
            if operation == "write":
                # Add extension if not present
                if not full_path.endswith(f".{file_format}"):
                    full_path = f"{full_path}.{file_format}"
                
                # Write content to file
                with open(full_path, 'w', encoding='utf-8') as f:
                    if file_format == "json":
                        json.dump(json.loads(content) if isinstance(content, str) else content, f, indent=2)
                    else:
                        f.write(content)
                
                return {
                    "success": True,
                    "message": f"File saved successfully: {full_path}",
                    "file_path": full_path
                }
            
            elif operation == "read":
                if not os.path.exists(full_path):
                    return {
                        "success": False,
                        "message": f"File not found: {full_path}"
                    }
                
                with open(full_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                
                return {
                    "success": True,
                    "file_path": full_path,
                    "content": file_content[:5000]  # Limit content
                }
            
            elif operation == "list":
                if not os.path.exists(full_path):
                    return {
                        "success": False,
                        "message": f"Directory not found: {full_path}"
                    }
                
                files = os.listdir(full_path)
                return {
                    "success": True,
                    "directory": full_path,
                    "files": files
                }
            
            else:
                return {
                    "success": False,
                    "message": f"Unknown operation: {operation}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"File operation failed: {str(e)}"
            }
