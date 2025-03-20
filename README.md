# minion-mobile

A Python library for AI-driven mobile device automation using LLMs to control Android devices.

## Installation

```bash
pip install minion-mobile
```

## Requirements

- Python 3.8+
- Android SDK with ADB configured
- Connected Android device or emulator

## Features

- AI-powered mobile automation
- Natural language instructions for mobile device control
- ADB integration for Android devices
- Screenshots and UI hierarchy inspection
- Touch, swipe, type, and other gesture control
- LLM-agnostic: works with any LLM provider

## Basic Usage

The library is designed to be LLM-agnostic, allowing you to use any LLM provider:

```python
import asyncio
from minion_mobile import mobile_use

# Define a function to call your preferred LLM
async def call_my_llm(messages, tools=None):
    # Implement your LLM calling logic here
    # This is just a placeholder
    return {
        "role": "assistant",
        "content": "I'll help automate your mobile device."
    }

async def main():
    # Use mobile_use with your LLM
    result = await mobile_use(
        task="Open the calculator app and press the number 5", 
        llm_function=call_my_llm
    )
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

## Integration with Minion

```python
import asyncio
import sys
from pathlib import Path

# Import mobile_use
from minion_mobile import mobile_use

# Add minion to path (if not installed via pip)
minion_path = Path('/path/to/minion')
sys.path.append(str(minion_path))

from minion.configs.config import config
from minion.providers import create_llm_provider
from minion.schema.message_types import Message

async def minion_llm_function(messages, tools=None):
    """Function to call minion LLM"""
    # Get model configuration
    model_name = "gpt-4o"  # or any other model you prefer
    llm_config = config.models.get(model_name)
    
    if not llm_config:
        raise ValueError(f"Model configuration for '{model_name}' not found")
    
    # Create LLM provider
    llm = create_llm_provider(llm_config)
    
    # Convert messages to Minion Message format
    minion_messages = [
        Message(role=msg["role"], content=msg["content"]) 
        for msg in messages
    ]
    
    # Generate response
    response = await llm.generate(minion_messages, tools=tools)
    return {
        "role": "assistant",
        "content": response
    }

async def main():
    # Use mobile_use with Minion
    result = await mobile_use(
        task="Open the calculator app and press the number 5", 
        llm_function=minion_llm_function
    )
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

## ADB Functions

The library provides direct access to ADB functionality:

```python
from minion_mobile import ADBClient

async def main():
    # Initialize ADB client
    adb = ADBClient()
    
    # Take a screenshot
    screenshot = await adb.screenshot()
    
    # Tap on the screen
    await adb.tap(500, 500)
    
    # Type text
    await adb.inputText("Hello, world!")
    
    # Press a key
    await adb.keyPress("KEYCODE_ENTER")
    
    # Get UI hierarchy
    ui = await adb.dumpUI()

if __name__ == "__main__":
    asyncio.run(main())
```

## Available Functions

- `screenshot()`: Take a screenshot of the device
- `tap()`: Tap at specific coordinates
- `swipe()`: Perform swipe gestures
- `inputText()`: Input text
- `keyPress()`: Press a specific key
- `dumpUI()`: Get the UI hierarchy for analysis
- `openApp()`: Open an application by package name

## License

MIT 