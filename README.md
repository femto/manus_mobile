# manus_mobile

A Python library for AI-driven mobile device automation using LLMs to control Android devices.

## Installation

```bash
pip install manus_mobile
```

## Requirements

- Python 3.8+
- Android SDK with ADB configured
- Connected Android device or emulator

## ADB Configuration

### Setting Up ADB Path

By default, the library looks for the `adb` command in your PATH. If ADB is installed in a non-standard location, you can specify the path:

```python
from manus_mobile import ADBClient

# Specify the path to the ADB binary
adb_path = "/path/to/android/sdk/platform-tools/adb"
adb = ADBClient(adb_path=adb_path)
```

### Using Environment Variable

You can also set the `ADB_PATH` environment variable:

```bash
# In your shell
export ADB_PATH="/path/to/android/sdk/platform-tools/adb"
```

```python
# In your Python code
import os
from manus_mobile import ADBClient

# Use ADB path from environment variable, or fall back to default
adb_path = os.environ.get("ADB_PATH", "adb")
adb = ADBClient(adb_path=adb_path)
```

### Using the Setup Script

The package includes a setup script to automatically configure ADB:

```bash
# Run the setup script
source setup_adb.sh
```

This script will:
1. Look for ADB in the default location
2. If not found, search in your PATH
3. If still not found, prompt you to enter the path manually
4. Add the configuration to your ~/.zshrc for permanent use

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
from manus_mobile import mobile_use

async def main():
    # Use mobile_use with a specific model name
    result = await mobile_use(
        task="Open the calculator app and press the number 5", 
        model_or_function="gpt-4o"  # Specify model name from minion config
    )
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

## Using Custom LLM Functions

If you prefer to use a custom LLM function, you can still pass it directly:

```python
import asyncio
import sys
from pathlib import Path

# Import mobile_use
from manus_mobile import mobile_use

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
        model_or_function=minion_llm_function  # Pass custom function
    )
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

## Model Selection

When using the string-based model parameter, you can specify any model name defined in your minion configuration:

```python
import asyncio
from manus_mobile import mobile_use

async def main():
    # Available models (depending on your minion config):
    # - "default" - uses the default model from minion config
    # - "gpt-4o"
    # - "gpt-4o-mini"
    # - "gemini-2.0-flash-exp"
    # - "deepseek-r1"
    # - "phi-4"
    # - "llama3.2"
    
    # Select your preferred model
    model = "gpt-4o"
    
    result = await mobile_use(
        task="Open the camera app and take a photo",
        model_or_function=model
    )
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

## ADB Functions

The library provides direct access to ADB functionality:

```python
from manus_mobile import ADBClient

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

- `screenshot()`: Take a screenshot of the device and return raw binary data that can be opened with PIL
- `tap()`: Tap at specific coordinates
- `swipe()`: Perform swipe gestures
- `inputText()`: Input text
- `keyPress()`: Press a specific key
- `dumpUI()`: Get the UI hierarchy for analysis
- `openApp()`: Open an application by package name

## Screenshot Example

```python
import asyncio
import io
from PIL import Image
from manus_mobile import ADBClient

async def take_screenshot():
    adb = ADBClient()
    
    # Take a screenshot and get raw binary data
    screenshot_data = await adb.screenshot()
    
    # Use PIL to process the image
    image = Image.open(io.BytesIO(screenshot_data))
    print(f"Screenshot size: {image.width} x {image.height}")
    
    # Save the screenshot
    image.save("screenshot.png")

if __name__ == "__main__":
    asyncio.run(take_screenshot())
```

## License

MIT 