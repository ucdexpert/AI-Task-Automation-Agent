from typing import Dict, List, Any
from app.tools.base import BaseTool
from app.tools.email_tool import EmailTool
from app.tools.web_scraper_tool import WebScraperTool
from app.tools.web_search_tool import WebSearchTool
from app.tools.file_tool import FileTool
from app.tools.google_calendar_tool import GoogleCalendarTool
from app.tools.google_drive_tool import GoogleDriveTool
from app.tools.whatsapp_tool import WhatsAppTool
from app.tools.calendar_notification_tool import CalendarNotificationTool
from app.tools.robot_tool import RobotTool

class ToolRegistry:
    """
    Registry for all available agent tools
    """
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        """Register default tools"""
        tools = [
            EmailTool(),
            WebScraperTool(),
            WebSearchTool(),
            FileTool(),
            GoogleCalendarTool(),
            GoogleDriveTool(),
            WhatsAppTool(),
            CalendarNotificationTool(),
            RobotTool()
        ]
        for tool in tools:
            self.register_tool(tool)
    
    def register_tool(self, tool: BaseTool):
        """Register a new tool"""
        self.tools[tool.name] = tool
    
    def get_tool(self, name: str) -> BaseTool:
        """Get tool by name"""
        if name not in self.tools:
            raise ValueError(f"Tool '{name}' not found")
        return self.tools[name]
    
    def get_all_tools(self) -> List[BaseTool]:
        """Get all registered tools"""
        return list(self.tools.values())
    
    def get_tools_schema(self) -> List[Dict[str, Any]]:
        """Get all tools schema for LLM function calling"""
        return [tool.get_schema() for tool in self.get_all_tools()]
    
    async def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Execute a tool by name with given parameters"""
        tool = self.get_tool(tool_name)
        return await tool.execute(**kwargs)

# Global registry instance
tool_registry = ToolRegistry()
