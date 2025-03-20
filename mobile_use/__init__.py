from typing import Dict, Any, Optional, Union
from langchain.schema import BaseMessage
from langchain.schema.runnable import RunnableConfig
from langchain.callbacks.manager import CallbackManager
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool
from langchain_anthropic import ChatAnthropic

# Export the ADBClient class
from .adb_client import ADBClient, Coordinate
from .mobile_computer import create_mobile_computer

__all__ = ["ADBClient", "mobile_use"]

class OpenAppToolArgs(BaseModel):
    name: str = Field(
        ..., 
        description="package name of the app to open such as com.google.android.dialer"
    )

class OpenAppTool(BaseTool):
    """Tool for opening apps on a mobile device."""
    
    name = "open_app"
    description = "Open an app on android device."
    args_schema = OpenAppToolArgs
    
    def __init__(self, adb_client: ADBClient):
        """Initialize with an ADB client."""
        super().__init__()
        self.adb_client = adb_client
    
    async def _arun(self, name: str) -> str:
        """Open the specified app by package name."""
        await self.adb_client.openApp(name)
        return f"Successfully opened {name}"

# Default system prompt for mobile automation
MOBILE_USE_PROMPT = """You are an experienced mobile automation engineer. 
Your job is to navigate an android device and perform actions to fulfill request of the user.

<steps>
If the user asks to use a specific app in the request, open it before performing any other action.
Do not take ui dump more than once per action. If you think you don't need to take ui dump, skip it. Use it sparingly.
</steps>
"""

async def mobile_use(task: str, llm: Optional[Any] = None) -> Dict[str, Any]:
    """
    Use AI to automate mobile device interactions.
    
    Args:
        task: The task description for the AI to perform
        llm: Optional language model (defaults to Anthropic's Claude)
        
    Returns:
        The result of the AI-driven mobile automation
    """
    # Initialize the ADB client
    adb_client = ADBClient()
    
    # Create the mobile computer tool
    computer = await create_mobile_computer(adb_client)
    
    # Create the open app tool
    open_app_tool = OpenAppTool(adb_client)
    
    # Set up the language model
    if llm is None:
        llm = ChatAnthropic(model_name="claude-3-7-sonnet-20250219")
    
    # Generate the response using the language model with tools
    response = await llm.invoke(
        [
            {"role": "system", "content": MOBILE_USE_PROMPT},
            {"role": "user", "content": task}
        ],
        config=RunnableConfig(
            callbacks=CallbackManager(),
        ),
        tools=[open_app_tool, computer]
    )
    
    return response 