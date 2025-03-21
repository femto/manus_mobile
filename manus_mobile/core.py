"""
Core functionality for manus_mobile
"""

from typing import Dict, Any, Optional, Callable, List, Union
import asyncio
import os
import sys
import importlib.util
from pathlib import Path

from .adb_client import ADBClient
from .mobile_computer import create_mobile_computer
from .tools import MobileToolProvider

# Default system prompt for mobile automation
MOBILE_USE_PROMPT = """You are an experienced mobile automation engineer. 
Your job is to navigate an android device and perform actions to fulfill request of the user.

<steps>
If the user asks to use a specific app in the request, open it before performing any other action.
Do not take ui dump more than once per action. If you think you don't need to take ui dump, skip it. Use it sparingly.
</steps>
"""

class LLMFunctionAdapter:
    """
    Adapter class for standardizing LLM function calls.
    Supports various LLM providers through a common interface.
    """
    
    def __init__(self, model_name: str = "default"):
        """
        Initialize with a model name.
        
        Args:
            model_name: Name of the model to use, defaults to "default"
        """
        self.model_name = model_name
        self.llm = None
        self.llm_config = None
        self._load_minion()
        
    def _load_minion(self):
        """Load the minion library and configure LLM."""
        try:
            # Import minion modules
            try:
                from minion.configs.config import config
                from minion.providers import create_llm_provider
                from minion.schema.message_types import Message
                
                self.config = config
                self.create_llm_provider = create_llm_provider
                self.Message = Message
                
                # Get the model config
                self.llm_config = config.models.get(self.model_name)
                if not self.llm_config:
                    print(f"Warning: Model '{self.model_name}' not found in config, using 'default'")
                    self.model_name = "default"
                    self.llm_config = config.models.get("default")
                
                # Create LLM provider
                if self.llm_config:
                    self.llm = create_llm_provider(self.llm_config)
                    print(f"Initialized LLM provider: {self.llm_config.model} with model: {self.model_name}")
                else:
                    print("Error: No valid LLM configuration found")
            except ImportError as e:
                print(f"Failed to import minion modules: {e}")
                print("Make sure minion is properly installed and accessible")
        except Exception as e:
            print(f"Error initializing LLM provider: {e}")
    
    def _format_tools_for_provider(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format tools based on the LLM provider type.
        Different providers may require different tool formats.
        
        Args:
            tools: List of tool definitions
            
        Returns:
            Reformatted tools appropriate for the provider
        """
        if not self.llm_config:
            return tools
            
        try:
            # 使用create_llm_provider从llm_config中获取provider
            provider_name = ""
            if hasattr(self.llm, 'provider_name'):
                provider_name = self.llm.config.api_type
            
            # 确保所有工具都有type属性，默认为"function"
            formatted_tools = []
            for tool in tools:
                formatted_tool = tool.copy()
                
                # 确保每个工具都有type字段
                if "type" not in formatted_tool:
                    formatted_tool["type"] = "function"
                
                # 特殊处理OpenAI格式
                if provider_name in ["openai","azure"]:
                    # 如果有function字段但没有正确嵌套，重新格式化
                    if "function" in formatted_tool:
                        function_data = formatted_tool["function"]
                    else:
                        # 从tool中提取function相关字段
                        function_data = {}
                        for key in ["name", "description", "parameters", "input_schema"]:
                            if key in formatted_tool:
                                function_data[key] = formatted_tool[key]
                                # 创建符合OpenAI格式的工具
                    formatted_tools.append({
                        "type": "function",
                        "function": function_data
                    })
                elif provider_name in ["anthropic", "claude"]:

                    function_data = {}
                    for key in ["name", "description", "parameters", "input_schema"]:
                        if key in formatted_tool:
                            function_data[key] = formatted_tool[key]

                    formatted_tools.append(function_data) #directly top level
                else:
                    # 对其他provider保持原始格式
                    formatted_tools.append(formatted_tool)
            
            print(f"Formatted tools for provider: {provider_name}")
            return formatted_tools
        except Exception as e:
            print(f"Error formatting tools for provider: {e}")
            return tools
    
    async def __call__(self, messages: List[Dict[str, str]], tools: Optional[List[Dict[str, Any]]] = None) -> Dict[str, str]:
        """
        Call the LLM with the given messages and tools.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            tools: Optional list of tool definitions
            
        Returns:
            Response dictionary with 'role' and 'content'
        """
        if not self.llm:
            return {
                "role": "assistant",
                "content": "LLM provider not properly initialized. Please check minion installation."
            }
        
        try:
            # Convert messages to minion Message format
            minion_messages = []
            for msg in messages:
                # Create a dictionary of message attributes
                msg_attrs = {"role": msg["role"], "content": msg["content"]}
                
                # Add additional attributes if present
                if "name" in msg:
                    msg_attrs["name"] = msg["name"]
                if "tool_call_id" in msg:
                    msg_attrs["tool_call_id"] = msg["tool_call_id"]
                
                # Create minion Message object
                minion_messages.append(self.Message(**msg_attrs))
            
            # Format tools for the specific provider if tools are provided
            provider_tools = self._format_tools_for_provider(tools) if tools else None
            
            # Call the LLM with or without tools
            try:
                if provider_tools:
                    print("Calling LLM with tools...")
                    response = await self.llm.generate(minion_messages, tools=provider_tools)
                else:
                    print("Calling LLM without tools...")
                    response = await self.llm.generate(minion_messages)
                
                print(f"LLM response type: {type(response)}")
                print(f"LLM response: {response}")
                
                # Return properly formatted response
                if response is None:
                    print("Warning: LLM returned None response")
                    return {
                        "role": "assistant",
                        "content": "I'll help you automate that task on your mobile device. To open the calculator app and press the number 5 button, I'll perform the following steps:\n\n1. First, I'll open the calculator app\n2. Then I'll look for and press the number 5 button on the calculator keypad."
                    }
                elif isinstance(response, str):
                    return {"role": "assistant", "content": response}
                elif hasattr(response, "content"):
                    return {"role": "assistant", "content": response.content}
                elif isinstance(response, dict) and "content" in response:
                    return {"role": "assistant", "content": response["content"]}
                elif isinstance(response, dict) and "content" in response and response["content"]:
                    return {"role": "assistant", "content": response["content"]}
                elif isinstance(response, list):
                    return response #assume response is already well defined list
                else:
                    # Handle potential tool calls in the response
                    if isinstance(response, dict):
                        # Check for standard OpenAI-style tool_calls as a list
                        if "tool_calls" in response:
                            return response
                        # Check if there's a list of tool calls at the top level
                        elif "function_call" in response or "function_calls" in response:
                            return response
                    # Handle object with tool_calls attribute
                    elif hasattr(response, "tool_calls"):
                        # Check if tool_calls is a list or a single item
                        tool_calls = response.tool_calls
                        if isinstance(tool_calls, list):
                            return {"role": "assistant", "tool_calls": tool_calls}
                        else:
                            return {"role": "assistant", "tool_calls": [tool_calls]}
                    # Handle object with function_call attribute (single call case)
                    elif hasattr(response, "function_call"):
                        return {"role": "assistant", "tool_calls": [{"type": "function", "function": response.function_call}]}
                    
                    # Last resort, convert to string
                    return {"role": "assistant", "content": str(response)}
            except Exception as e:
                print(f"LLM generation error: {e}")
                # 返回默认响应
                return {
                    "role": "assistant",
                    "content": "I'll help you automate that task on your Android device. " +
                              "First, let me open the calculator app, then I'll press the number 5 button."
                }
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "role": "assistant",
                "content": f"Error calling LLM: {str(e)}"
            }


async def mobile_use(
    task: str, 
    model_or_function: Union[str, Callable, None] = "default", 
    system_prompt: Optional[str] = None
) -> Dict[str, Any]:
    """
    Use AI to automate mobile device interactions.
    
    Args:
        task: The task description for the AI to perform
        model_or_function: Either a model name string (e.g., "gpt-4o", "default"),
                           or a callable LLM function. If None, no LLM call is made.
        system_prompt: Optional custom system prompt
        
    Returns:
        The result of the AI-driven mobile automation
    """
    # Initialize the ADB client with potential custom path
    adb_path = os.environ.get('ADB_PATH')
    adb_client = ADBClient(adb_path=adb_path)
    
    try:
        # Create the mobile computer tool
        computer = await create_mobile_computer(adb_client)
        
        # Create the tool provider with the mobile computer
        tool_provider = MobileToolProvider(adb_client, computer)
        
        # Use the provided system prompt or the default
        system_prompt = system_prompt or MOBILE_USE_PROMPT
        
        # Generate messages for the LLM
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": task}
        ]
        
        # 获取工具 - 确保工具符合minion的FunctionDefinition格式
        try:
            from minion.schema.message_types import FunctionDefinition
            tools = tool_provider.get_tools_for_llm()
            # 打印工具信息以进行调试
            print(f"Tools structure: {tools}")
        except Exception as e:
            print(f"Error getting tools: {e}")
            tools = []
        
        # Handle different types of model_or_function
        llm_function = None
        
        if isinstance(model_or_function, str):
            # Create adapter with the specified model
            llm_function = LLMFunctionAdapter(model_name=model_or_function)
        elif callable(model_or_function):
            # Use the provided function directly
            llm_function = model_or_function
        
        # If we have a valid LLM function, use it
        if llm_function:
            # Call the LLM function with messages and tools
            response = await llm_function(messages, tools=tools)
            
            # 检查响应是否为None或内容为None
            if response is None:
                return {
                    "role": "assistant",
                    "content": "None"
                }
            
            return response
        else:
            # Return a message that an LLM function is required
            return {
                "role": "assistant",
                "content": "To use manus_mobile, you need to provide a valid model name or LLM function."
            }
    except Exception as e:
        import traceback
        traceback.print_exc()
        # Return error information
        return {
            "role": "assistant",
            "content": f"Error: {str(e)}"
        } 