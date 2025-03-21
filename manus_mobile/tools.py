"""
Tool providers and utilities for manus_mobile
"""

from typing import Dict, Any, List
from .adb_client import ADBClient
from .mobile_computer import MobileComputer

class MobileToolProvider:
    """Provider for mobile automation tools."""
    
    def __init__(self, adb_client: ADBClient, mobile_computer: MobileComputer = None):
        """Initialize with an ADB client and optional mobile computer."""
        self.adb_client = adb_client
        self.mobile_computer = mobile_computer
        self.tools = {}
        self._setup_tools()
    
    def _setup_tools(self):
        """Set up the available tools."""
        # Open app tool
        self.tools["open_app"] = {
            "name": "open_app",
            "description": "Open an app on android device.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "package name of the app to open such as com.google.android.dialer"
                    }
                },
                "required": ["name"]
            },
            "function": self._open_app
        }
        
        # If we have a mobile computer, add mobile_computer tool
        if self.mobile_computer:
            self.tools["mobile_computer"] = {
                "name": "mobile_computer",
                "description": "Mobile tool to perform actions on a mobile device.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["dump_ui", "tap", "swipe", "type", "press", "screenshot"],
                            "description": "The action to perform on the mobile device"
                        },
                        "coordinate": {
                            "type": "array",
                            "items": {"type": "integer"},
                            "description": "The x, y coordinates for tapping on the screen"
                        },
                        "start_coordinate": {
                            "type": "array",
                            "items": {"type": "integer"},
                            "description": "The starting x, y coordinates for a swipe gesture"
                        },
                        "end_coordinate": {
                            "type": "array",
                            "items": {"type": "integer"},
                            "description": "The ending x, y coordinates for a swipe gesture"
                        },
                        "text": {
                            "type": "string",
                            "description": "Text to type or a key to press"
                        },
                        "duration": {
                            "type": "integer",
                            "description": "Duration for operations like swipes in milliseconds"
                        }
                    },
                    "required": ["action"]
                },
                "function": self._mobile_computer
            }
    
    async def _open_app(self, name: str) -> str:
        """Open the specified app by package name."""
        await self.adb_client.openApp(name)
        return f"Successfully opened {name}"
    
    async def _mobile_computer(self, **kwargs) -> str:
        """Execute mobile computer commands."""
        if self.mobile_computer:
            return await self.mobile_computer.execute(**kwargs)
        return "Error: Mobile computer not initialized"
    
    def get_tools_for_llm(self) -> List[Dict[str, Any]]:
        """Get tools description for LLM."""
        # 无论是否在minion环境中，都使用OpenAI格式的工具
        tools = []
        
        for tool_name, tool_info in self.tools.items():
            # 确保parameters有正确的结构
            parameters = tool_info["parameters"]
            if "type" not in parameters:
                parameters["type"] = "object"
            if "properties" not in parameters:
                parameters["properties"] = {}
            if "required" not in parameters:
                parameters["required"] = []
                
            # 始终使用OpenAI格式的工具定义
            tools.append({
                "type": "function",
                "function": {
                    "name": tool_name,
                    "description": tool_info["description"],
                    "parameters": parameters
                }
            })
            
        print(f"Created {len(tools)} tools in OpenAI format")
        return tools

    async def execute_tool(self, tool_name: str, **kwargs) -> str:
        """Execute a tool with the given arguments."""
        if tool_name not in self.tools:
            return f"Error: Tool '{tool_name}' not found."
        
        try:
            result = await self.tools[tool_name]["function"](**kwargs)
            return result
        except Exception as e:
            return f"Error executing {tool_name}: {str(e)}" 