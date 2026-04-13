from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class BaseTool(ABC):
    """
    Base class for all agent tools
    """
    name: str
    description: str
    
    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the tool with given parameters
        """
        pass
    
    def get_schema(self) -> Dict[str, Any]:
        """
        Return tool schema for LLM function calling
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": self.get_parameters_schema(),
                    "required": self.get_required_parameters()
                }
            }
        }
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        """
        Return parameters schema (override in child classes)
        """
        return {}
    
    def get_required_parameters(self) -> list:
        """
        Return list of required parameters
        """
        return []
