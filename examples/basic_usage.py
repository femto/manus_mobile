import asyncio
import sys
import os

from manus_mobile import mobile_use, ADBClient

# ADB path configuration
ADB_PATH = os.environ.get('ADB_PATH', '/Users/femtozheng/Library/Android/sdk/platform-tools/adb')

async def main():
    """
    Example demonstrating basic usage of the mobile_use package.
    
    This will use an AI agent to perform tasks on a connected Android device.
    Ensure you have an Android device connected via ADB before running.
    """
    print("Starting mobile automation...")
    
    # Configure ADB path for the session
    os.environ['ADB_PATH'] = ADB_PATH
    print(f"Using ADB from: {ADB_PATH}")
    
    # Check if device is connected
    adb = ADBClient(adb_path=ADB_PATH)
    devices = await adb.getDevices()
    if not devices:
        print("No Android devices found. Please connect a device and try again.")
        return
    
    print(f"Connected devices: {devices}")
    
    # 指定使用特定设备 (使用 -s emulator-5556 参数)
    os.environ['ANDROID_SERIAL'] = 'emulator-5554'
    print(f"Using device: emulator-5554")
    
    # Define a task for the AI to perform
    task = "Open the calculator app and press the number 5 button"
    
    # Select which model to use - 使用支持的模型名称
    # Available models: "default", "gpt-4o", "gpt-4o-mini", "gemini-2.0-flash-exp", "deepseek-r1", "phi-4", "llama3.2"
    model = "gpt-4o"
    
    try:
        # Run the automation with the specified model
        print(f"Using model: {model}")
        result = await mobile_use(task=task, model_or_function=model)
        
        # Display the result
        print("\nAI Response:")
        print(result)
        
        print("\nAutomation completed successfully!")
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure you have an Android device connected via ADB.")

if __name__ == "__main__":
    asyncio.run(main()) 