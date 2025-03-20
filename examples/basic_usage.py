import asyncio
import sys
import os

# Add the parent directory to the Python path to allow importing the local package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mobile_use import mobile_use

async def main():
    """
    Example demonstrating basic usage of the mobile_use package.
    
    This will use an AI agent to perform tasks on a connected Android device.
    Ensure you have an Android device connected via ADB before running.
    """
    print("Starting mobile automation...")
    
    # Define a task for the AI to perform
    task = "Open the calculator app and press the number 5 button"
    
    try:
        # Run the automation
        result = await mobile_use(task=task)
        
        # Display the result
        print("\nAI Response:")
        print(result)
        
        print("\nAutomation completed successfully!")
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure you have an Android device connected via ADB.")

if __name__ == "__main__":
    asyncio.run(main()) 