#!/bin/bash
# Activation script for affordability_website virtual environment

# Navigate to the project directory
cd "$(dirname "$0")"

# Activate the virtual environment
source venv/bin/activate

echo "✓ Virtual environment activated!"
echo "Python: $(which python)"
echo "Python version: $(python --version)"
echo ""
echo "To generate figures, run:"
echo "  python generate_figures.py"
echo ""
echo "To deactivate the virtual environment, run:"
echo "  deactivate"
