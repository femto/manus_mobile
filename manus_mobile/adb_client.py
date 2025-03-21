import subprocess
import json
import base64
import os
from typing import Dict, List, Optional, Tuple, Union
import asyncio

class Coordinate:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

# Dictionary mapping key names to Android key event codes
ANDROID_KEY_EVENTS = {
    "Enter": "KEYCODE_ENTER",
    "Backspace": "KEYCODE_DEL",
    "Tab": "KEYCODE_TAB",
    "ArrowUp": "KEYCODE_DPAD_UP",
    "ArrowDown": "KEYCODE_DPAD_DOWN",
    "ArrowLeft": "KEYCODE_DPAD_LEFT",
    "ArrowRight": "KEYCODE_DPAD_RIGHT",
    "Escape": "KEYCODE_ESCAPE",
    "Home": "KEYCODE_HOME",
}

class ADBClient:
    def __init__(self, adb_path: str = None):
        # Use provided adb_path or default to 'adb' command
        self.adb_path = adb_path or 'adb'
        
        # Validate ADB is available
        try:
            subprocess.run([self.adb_path, "version"], check=True, capture_output=True)
        except (subprocess.SubprocessError, FileNotFoundError):
            raise RuntimeError(f"ADB is not available at path: {self.adb_path}. Please install Android SDK and set up ADB.")

    def _execute_adb_command(self, command: str) -> subprocess.CompletedProcess:
        """Execute an ADB command and return the completed process."""
        full_command = f"{self.adb_path} {command}"
        result = subprocess.run(
            full_command, 
            shell=True, 
            capture_output=True, 
            text=True
        )
        return result

    def _shell(self, command: str) -> Dict[str, str]:
        """Execute an ADB shell command."""
        result = self._execute_adb_command(f"shell {command}")
        return {
            "stdout": result.stdout,
            "stderr": result.stderr
        }

    async def screenshot(self) -> bytes:
        """Take a screenshot of the device and return as bytes."""
        # Execute the screenshot command and capture binary output directly
        full_command = f"{self.adb_path} shell screencap -p"
        process = await asyncio.create_subprocess_shell(
            full_command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        # Return the raw binary data
        return stdout

    async def screenSize(self) -> Dict[str, int]:
        """Get the screen size of the device."""
        result = self._shell("wm size")
        stdout = result["stdout"]
        match = next((line for line in stdout.split('\n') if "Physical size" in line), None)
        
        if not match:
            raise RuntimeError("Failed to get screen size")
            
        # Extract dimensions using string operations
        dimensions = match.split("Physical size:")[1].strip().split("x")
        return {
            "width": int(dimensions[0]),
            "height": int(dimensions[1])
        }

    async def shell(self, command: str) -> Dict[str, str]:
        """Execute a shell command on the device."""
        return self._shell(command)

    async def doubleTap(self, coordinate: Coordinate) -> Dict[str, str]:
        """Double tap at the specified coordinate."""
        self._shell(f"input tap {coordinate.x} {coordinate.y}")
        return self._shell(f"input tap {coordinate.x} {coordinate.y}")

    async def tap(self, coordinate: Coordinate) -> Dict[str, str]:
        """Tap at the specified coordinate."""
        return self._shell(f"input tap {coordinate.x} {coordinate.y}")

    async def swipe(self, start: Coordinate, end: Coordinate, duration: int = 300) -> Dict[str, str]:
        """Swipe from start to end coordinates with specified duration."""
        return self._shell(
            f"input swipe {start.x} {start.y} {end.x} {end.y} {duration}"
        )

    async def type(self, text: str) -> Dict[str, str]:
        """Type the specified text."""
        # Escape special characters in text
        escaped_text = text.replace(' ', '\ ').replace('"', '\"')
        return self._shell(f'input text "{escaped_text}"')

    async def keyPress(self, key: str) -> Dict[str, str]:
        """Press the specified key."""
        android_key = ANDROID_KEY_EVENTS.get(key)
        if not android_key:
            raise ValueError(f"Unsupported key: {key}")
        
        return self._shell(f"input keyevent {android_key}")

    async def getDevices(self) -> List[str]:
        """Get a list of connected devices."""
        result = self._execute_adb_command("devices")
        devices = []
        
        # Parse the output to extract device IDs
        lines = result.stdout.strip().split('\n')
        if len(lines) > 1:  # Skip the first line (header)
            for line in lines[1:]:
                if line.strip():
                    device_id = line.split('\t')[0].strip()
                    devices.append(device_id)
                    
        return devices
        
    async def getCurrentApp(self) -> Dict:
        """Get the current foreground app information."""
        result = self._shell("dumpsys window | grep -E 'mCurrentFocus|mFocusedApp'")
        
        current_focus = None
        focused_app = None
        
        for line in result["stdout"].split('\n'):
            if "mCurrentFocus" in line and "/" in line:
                parts = line.split('/')
                if len(parts) >= 2:
                    package_activity = parts[0].split(' ')[-1] + "/" + parts[1].split(' ')[0]
                    current_focus = package_activity
                
            if "mFocusedApp" in line and "/" in line:
                parts = line.split('/')
                if len(parts) >= 2:
                    package_activity = parts[0].split(' ')[-1] + "/" + parts[1].split(' ')[0]
                    focused_app = package_activity
        
        return {
            "currentFocus": current_focus,
            "focusedApp": focused_app
        }

    async def listPackages(self, filter: Optional[str] = None) -> List[str]:
        """List installed packages, optionally filtered."""
        filter_arg = f" {filter}" if filter else ""
        result = self._shell(f"pm list packages{filter_arg}")
        
        packages = [
            line.replace("package:", "").strip()
            for line in result["stdout"].split("\n")
            if line.strip().startswith("package:")
        ]
        
        return packages

    async def openApp(self, packageName: str) -> Dict[str, str]:
        """Open an app using its package name."""
        result = self._shell(f"monkey -p {packageName} 1")
        
        if result["stderr"] and "No activities found" in result["stderr"]:
            raise RuntimeError(f"Failed to open app: {result['stderr']}")
            
        return result

    async def dumpUI(self) -> str:
        """Dump the UI hierarchy and return as JSON."""
        try:
            # Create the UI dump
            self._shell("uiautomator dump")
            
            # Read the dump file
            result = self._shell("cat /sdcard/window_dump.xml")
            
            # Clean up
            self._shell("rm /sdcard/window_dump.xml")
            
            # Convert XML to simple dictionary structure
            # In a real implementation, you'd need to parse XML properly
            # For this example, we're returning a placeholder
            xml_data = result["stdout"]
            
            # This would be replaced with proper XML parsing to JSON
            # Since we don't have the ui_dump_parser module yet
            parsed_data = self._simple_parse_ui(xml_data)
            
            return json.dumps(parsed_data)
        except Exception as e:
            raise RuntimeError(f"Failed to get UI hierarchy: {str(e)}")
    
    def _simple_parse_ui(self, xml_data: str) -> Dict:
        """
        Simple placeholder parser that extracts basic info from UI dump XML.
        In a real implementation, this would be more comprehensive.
        """
        # This is a simplified version - in reality you'd want a proper XML parser
        elements = []
        
        for line in xml_data.split("\n"):
            if 'bounds="' in line:
                # Extract some basic information
                bounds = line.split('bounds="')[1].split('"')[0]
                text = line.split('text="')[1].split('"')[0] if 'text="' in line else ""
                resource_id = line.split('resource-id="')[1].split('"')[0] if 'resource-id="' in line else ""
                
                elements.append({
                    "bounds": bounds,
                    "text": text,
                    "resource-id": resource_id
                })
        
        return {"elements": elements} 