#!/bin/bash

# Start the SaaS Metrics Dashboard
echo "Starting SaaS Metrics Dashboard..."

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "Error: Python is not installed or not in PATH"
    exit 1
fi

# Check if required files exist
if [ ! -f "app.py" ]; then
    echo "Error: app.py not found"
    exit 1
fi

if [ ! -f ".env" ]; then
    echo "Warning: .env file not found. Make sure environment variables are set."
fi

# Start the Flask application
echo "Starting Flask server on http://localhost:5002"
echo "Press Ctrl+C to stop the server"
echo ""

python app.py 