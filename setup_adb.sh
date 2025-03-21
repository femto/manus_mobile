#!/bin/bash

# Default ADB path on macOS
DEFAULT_ADB_PATH="/Users/femtozheng/Library/Android/sdk/platform-tools/adb"

# Check if ADB exists at the default location
if [ -f "$DEFAULT_ADB_PATH" ]; then
    echo "Found ADB at default location: $DEFAULT_ADB_PATH"
    export ADB_PATH="$DEFAULT_ADB_PATH"
else
    # Try to find adb in PATH
    ADB_IN_PATH=$(which adb)
    if [ -n "$ADB_IN_PATH" ]; then
        echo "Found ADB in PATH: $ADB_IN_PATH"
        export ADB_PATH="$ADB_IN_PATH"
    else
        echo "ADB not found in default location or PATH."
        echo "Please specify the path to ADB:"
        read -r user_path
        
        if [ -f "$user_path" ]; then
            echo "Using ADB at: $user_path"
            export ADB_PATH="$user_path"
        else
            echo "Invalid ADB path. ADB not found at: $user_path"
            exit 1
        fi
    fi
fi

# Add to .zshrc if not already there
if ! grep -q "export ADB_PATH=" ~/.zshrc; then
    echo "# ADB path for manus_mobile" >> ~/.zshrc
    echo "export ADB_PATH=\"$ADB_PATH\"" >> ~/.zshrc
    echo "Added ADB_PATH to ~/.zshrc"
fi

echo ""
echo "ADB is configured for manus_mobile:"
echo "ADB_PATH=$ADB_PATH"
echo ""
echo "To use in the current shell, run:"
echo "source setup_adb.sh"
echo ""
echo "To make this permanent, the setting has been added to your ~/.zshrc"
echo "Restart your terminal or run 'source ~/.zshrc' to apply." 