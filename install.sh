#!/bin/bash

# Exit on error
set -e

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Add current directory to PYTHONPATH to make the package importable
export PYTHONPATH=$PYTHONPATH:$(pwd)

echo ""
echo "Installation complete!"
echo ""
echo "To use the mobile_use package, activate the virtual environment with:"
echo "    source venv/bin/activate"
echo ""
echo "Then you can run the example with:"
echo "    python examples/basic_usage.py"
echo "" 