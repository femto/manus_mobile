"""
manus_mobile - Python library for AI-driven mobile device automation
"""

# Import typing classes
from typing import List, Dict, Any, Optional, Callable

# Export main classes and functions
from .adb_client import ADBClient, Coordinate
from .core import mobile_use, MOBILE_USE_PROMPT
from .tools import MobileToolProvider
from .mobile_computer import create_mobile_computer, MobileComputer

__version__ = "0.1.0"
__all__ = [
    "ADBClient", 
    "Coordinate", 
    "mobile_use", 
    "MobileToolProvider",
    "MOBILE_USE_PROMPT",
    "create_mobile_computer",
    "MobileComputer"
]