#!/bin/bash

# Health API Service - Run Script
echo "Starting Health API Service..."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Virtual environment not found!"
    echo "Please run: python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment and start server
source .venv/bin/activate
echo "Virtual environment activated"

echo "Starting server on http://localhost:8000"
echo "API Documentation will be available at:"
echo "   - Swagger UI: http://localhost:8000/docs"
echo ""
echo "Test the health endpoint: curl http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop the server"

# Start the FastAPI server
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
