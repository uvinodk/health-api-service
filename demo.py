#!/usr/bin/env python3
"""
Demo script for the Health API Service
This script demonstrates how to run and test the API
"""

import subprocess
import time
import requests
import sys
import os

def start_server():
    """Start the FastAPI server"""
    print("Starting Health API Service...")
    
    # Get the Python executable path
    venv_python = "/Users/vinodkumarudayakumar/Workspace/ee/health-api-service/.venv/bin/python"
    
    if not os.path.exists(venv_python):
        print("Virtual environment not found. Please run: pip install -r requirements.txt")
        return None
    
    # Start the server
    process = subprocess.Popen([
        venv_python, "-m", "uvicorn", "main:app", 
        "--host", "0.0.0.0", "--port", "8000"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait a moment for server to start
    time.sleep(3)
    
    return process

def test_health_endpoint():
    """Test the health endpoint"""
    print("\nTesting Health Endpoint...")
    
    try:
        response = requests.get("http://localhost:8000/health")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Health Check Successful!")
            print(f"   Status: {data['status']}")
            print(f"   Timestamp: {data['timestamp']}")
        else:
            print(f"Health Check Failed! Status Code: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("Could not connect to the server. Make sure it's running on port 8000.")
    except Exception as e:
        print(f"Error testing endpoint: {str(e)}")

def show_documentation_info():
    """Show information about API documentation"""
    print("\nAPI Documentation:")
    print("   Swagger UI: http://localhost:8000/docs")
    print("   OpenAPI JSON: http://localhost:8000/openapi.json")

def main():
    """Main demo function"""
    print("=" * 50)
    print("    Health API Service Demo")
    print("=" * 50)
    
    # Start server
    process = start_server()
    
    if process is None:
        return
    
    try:
        # Test the endpoint
        test_health_endpoint()
        
        # Show documentation info
        show_documentation_info()
        
        print("\nDemo completed successfully!")
        print("\nNext steps:")
        print("   1. Visit http://localhost:8000/health to see the API response")
        print("   2. Visit http://localhost:8000/docs for interactive API documentation")
        print("   3. Run tests with: pytest tests/ -v")
        print("\nPress Ctrl+C to stop the server")
        
        # Keep server running
        process.wait()
        
    except KeyboardInterrupt:
        print("\nStopping server...")
        process.terminate()
        process.wait()
        print("Server stopped successfully!")

if __name__ == "__main__":
    main()