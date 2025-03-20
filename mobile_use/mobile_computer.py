from typing import Dict, List, Any, Optional, Union
import base64
import json
from langchain.tools import BaseTool
from langchain.pydantic_v1 import BaseModel, Field

from .adb_client import ADBClient, Coordinate

class ComputerToolArgs(BaseModel):
    action: str = Field(
        ..., 
        description="The action to perform on the mobile device"
    )
    coordinate: Optional[List[int]] = Field(
        None, 
        description="The x, y coordinates for tapping on the screen"
    )
    start_coordinate: Optional[List[int]] = Field(
        None, 
        description="The starting x, y coordinates for a swipe gesture"
    )
    end_coordinate: Optional[List[int]] = Field(
        None, 
        description="The ending x, y coordinates for a swipe gesture"
    )
    text: Optional[str] = Field(
        None, 
        description="Text to type or a key to press"
    )
    duration: Optional[int] = Field(
        None, 
        description="Duration for operations like swipes in milliseconds"
    )

class MobileComputer(BaseTool):
    """Tool for interacting with a mobile device."""
    
    name = "mobile_computer"
    description = """Mobile tool to perform actions on a mobile device.
You have the following actions:
dump_ui: Use this action to get current screen and associated UI elements that you can interact with.
tap: Use this to tap. You need to provide coordinate.
swipe: Use this to swipe. You need to provide start_coordinate and end_coordinate to start your swipe to end.
type: Use this to type what you want to. Provide what you want to type in text.
press: Any key you want to press. Provide the key as text.
screenshot: Take a screenshot of the current screen.
"""
    args_schema = ComputerToolArgs

    def __init__(self, adb_client: ADBClient, height: int, width: int):
        """Initialize the mobile computer with screen dimensions."""
        super().__init__()
        self.adb_client = adb_client
        self.height = height
        self.width = width
    
    async def _arun(self, 
                   action: str,
                   coordinate: Optional[List[int]] = None,
                   start_coordinate: Optional[List[int]] = None,
                   end_coordinate: Optional[List[int]] = None,
                   text: Optional[str] = None,
                   duration: Optional[int] = None) -> Union[str, Dict[str, Any]]:
        """Execute the specified mobile action asynchronously."""
        
        if action == "dump_ui":
            return await self.adb_client.dumpUI()
            
        if action == "tap" and coordinate:
            x, y = coordinate
            await self.adb_client.tap(Coordinate(x, y))
            return await self.adb_client.dumpUI()
            
        if action == "press" and text:
            await self.adb_client.keyPress(text)
            return await self.adb_client.dumpUI()
            
        if action == "type" and text:
            await self.adb_client.type(text)
            return await self.adb_client.dumpUI()
            
        if action == "screenshot":
            screenshot = await self.adb_client.screenshot()
            return {
                "data": base64.b64encode(screenshot).decode("utf-8"),
                "type": "image/png"
            }
            
        if action == "swipe" and start_coordinate and end_coordinate:
            start_x, start_y = start_coordinate
            end_x, end_y = end_coordinate
            await self.adb_client.swipe(
                Coordinate(start_x, start_y),
                Coordinate(end_x, end_y),
                duration or 300
            )
            return await self.adb_client.dumpUI()
            
        # If we reach here, the action was invalid or missing required parameters
        return f"Error: Invalid action '{action}' or missing required parameters"

async def create_mobile_computer(adb_client: ADBClient) -> MobileComputer:
    """
    Factory function to create a mobile computer tool with proper screen dimensions.
    
    Args:
        adb_client: An initialized ADBClient
        
    Returns:
        A configured MobileComputer tool
    """
    # Get screen dimensions
    viewport_size = await adb_client.screenSize()
    
    # Create and return the tool
    return MobileComputer(
        adb_client=adb_client,
        height=viewport_size["height"],
        width=viewport_size["width"]
    ) 