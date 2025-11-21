# Health API Service

A simple FastAPI-based health check service that provides basic system health monitoring.

## Features

- REST API with health check endpoint
- System metrics (CPU, memory, disk, uptime)
- Unit tests with pytest
- OpenAPI/Swagger documentation

## API Endpoints

### GET /health

Returns the health status of the application with system metrics.

**Response Format:**
```json
{
  "status": "Healthy",
  "timestamp": "2025-10-05T17:41:13Z",
  "uptime": {
    "seconds": 166.11,
    "human_readable": "2m 46s"
  },
  "system": {
    "cpu_usage_percent": 13.6,
    "memory": {
      "used_percent": 66.8,
      "available_gb": 7.96
    },
    "disk": {
      "used_percent": 2.3,
      "free_gb": 365.91
    }
  }
}
```

**Status Codes:**
- `200` - OK: Service is healthy
- `500` - Internal Server Error: Service encountered an error

## Quick Start

### Prerequisites

- Python 3.7+
- pip

### Installation

1. Clone the repository:
```bash
git clone https://github.com/uvinodk/health-api-service.git
cd health-api-service
```

2. Create and activate virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

This installs:
- FastAPI and Uvicorn for the web server
- pytest and httpx for testing
- psutil for system metrics collection

### Running the Application

#### Option 1: Using the run script
```bash
./run.sh
```

#### Option 2: Running the demo script
```bash
python demo.py
```

The API will be available at: http://localhost:8000

## Testing

Run the unit tests:
```bash
pytest tests/ -v
```

Test the health endpoint manually:
```bash
curl http://localhost:8000/health
```

Example response:
```json
{
  "status": "Healthy",
  "timestamp": "2025-10-05T17:41:13Z",
  "uptime": {"seconds": 166.11, "human_readable": "2m 46s"},
  "system": {
    "cpu_usage_percent": 13.6,
    "memory": {"used_percent": 66.8, "available_gb": 7.96},
    "disk": {"used_percent": 2.3, "free_gb": 365.91}
  }
}
```

## API Documentation

Once the server is running, you can access the interactive API documentation:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **OpenAPI JSON**: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

## Project Structure

```
health-api-service/
├── main.py              # Main FastAPI application
├── requirements.txt     # Python dependencies
├── run.sh              # Shell script to start the server
├── demo.py             # Demo script with testing
├── tests/              # Unit tests directory
│   ├── __init__.py
│   └── test_health.py  # Health endpoint tests
└── README.md           # This file
```

## Health Check Response

The health endpoint provides comprehensive system information:

### Core Fields
- **status**: Always returns "Healthy" when the service is operational
- **timestamp**: ISO 8601 formatted UTC timestamp of when the check was performed

### Enhanced Metrics
- **uptime**: Application uptime in seconds and human-readable format
- **system**: Real-time system performance metrics
  - **cpu_usage_percent**: Current CPU utilization
  - **memory**: Memory usage percentage and available GB
  - **disk**: Disk usage percentage and free GB

### Docker

Run the build command from the project root
```
docker build -t health-api:latest .
```

Run container
```
docker run -d -p 8000:8000 --name health-api health-api:latest
```

Check health endpoint
```
curl http://localhost:8000/health
```

Using docker compose
```
docker-compose up --build
```

### Kubernetes

#### Local Development with Minikube

Prerequisites:
- Minikube installed on your local machine
- Docker installed
- kubectl installed

Start Minikube:
```bash
minikube start
```

Deploy to Minikube:
```bash
kubectl apply -f k8s/
kubectl get pods -n health-api
```

Load Docker image into Minikube:
```bash
# Build the image
docker build -t health-api:latest .

# Load the image into Minikube
minikube image load health-api:latest

# Update the deployment to use the local image if needed
kubectl set image deployment/health-api -n health-api health-api=health-api:latest
```

Access the service:
```bash
minikube service health-api -n health-api --url
# Or use port-forwarding
kubectl port-forward -n health-api svc/health-api 8000:8000
curl http://localhost:8000/health
```

Scale the deployment:
```bash
kubectl scale deployment health-api -n health-api --replicas=5
kubectl get pods -n health-api -w
```

#### CI/CD with Self-Hosted Runner

This project uses GitHub Actions with a self-hosted runner to deploy to a local Minikube cluster.

Setting up a self-hosted runner:
1. On GitHub, go to your repository settings
2. Navigate to Actions > Runners
3. Click "New self-hosted runner"
4. Follow the instructions to download and configure the runner on your local machine
5. Make sure the runner has access to your local Minikube cluster

The CI/CD pipeline will:
1. Run tests and code quality checks
2. Build and push the Docker image to GitHub Container Registry
3. Deploy the application to your local Minikube cluster using the self-hosted runner
