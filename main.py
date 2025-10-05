from fastapi import FastAPI, HTTPException
from datetime import datetime
import logging
import psutil
import platform
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Track application startup time
APP_START_TIME = time.time()

# Create FastAPI app instance
app = FastAPI(
    title="Health API Service",
    description="A simple health check API service",
    version="1.0.0"
)

@app.get("/health")
async def health_check():
    """
    Health check endpoint that returns the status and system metrics.
    
    Returns:
        dict: JSON response with status, timestamp, and system metrics
    """
    try:
        current_time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        
        # Calculate uptime
        uptime_seconds = time.time() - APP_START_TIME
        
        # Get system metrics
        memory = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=None)
        disk = psutil.disk_usage('/')
        
        response = {
            "status": "Healthy",
            "timestamp": current_time,
            "uptime": {
                "seconds": round(uptime_seconds, 2),
                "human_readable": format_uptime(uptime_seconds)
            },
            "system": {
                "cpu_usage_percent": round(cpu_percent, 1),
                "memory": {
                    "used_percent": round(memory.percent, 1),
                    "available_gb": round(memory.available / (1024**3), 2)
                },
                "disk": {
                    "used_percent": round((disk.used / disk.total) * 100, 1),
                    "free_gb": round(disk.free / (1024**3), 2)
                }
            },
            "environment": {
                "python_version": platform.python_version(),
                "platform": platform.system(),
                "hostname": platform.node()
            }
        }
        
        logger.info(f"Health check completed - CPU: {cpu_percent}%, Memory: {memory.percent}%")
        return response
    
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

def format_uptime(seconds):
    """Format uptime in human readable format"""
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)