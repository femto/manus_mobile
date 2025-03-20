# mobile_use

A Python library for AI-driven mobile device automation using LLMs to control Android devices.

## Installation

```bash
pip install mobile_use
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

## Usage

```python
from mobile_use import mobile_use
from anthropic import Anthropic

# Initialize the client
result = await mobile_use(
    task="Open the calculator app and press the number 5", 
    llm=Anthropic().messages
)
```

## Functions

- `screenshot()`: Take a screenshot of the device
- `tap()`: Tap at specific coordinates
- `swipe()`: Perform swipe gestures
- `type()`: Input text
- `keyPress()`: Press a specific key
- `dumpUI()`: Get the UI hierarchy for analysis
- `openApp()`: Open an application by package name

## License

MIT 