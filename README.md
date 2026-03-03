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

### Helm

Deploy using Helm:
```bash
helm install health-api ./helm
```

Deploy with custom values:
```bash
helm install health-api ./helm --set replicaCount=5
```

Upgrade deployment:
```bash
helm upgrade health-api ./helm
```

Uninstall:
```bash
helm uninstall health-api
```

Check deployment:
```bash
kubectl get all -n health-api
```

## AWS Deployment

### Prerequisites

- AWS account with appropriate permissions
- Terraform >= 1.3
- kubectl configured with AWS credentials
- GitHub repository with this code
- S3 bucket for Terraform state (configure in `terraform/provider.tf`)

### Infrastructure Setup

1. **Create Terraform state backend:**

```bash
# Create S3 bucket for state
aws s3 mb s3://health-api-tfstate-ACCOUNT_ID

# Create DynamoDB table for state locking
aws dynamodb create-table \
  --table-name health-api-tfstate-lock \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5
```

2. **Update `terraform/provider.tf`:**

Replace `REPLACE_TFSTATE_BUCKET` and `REPLACE_TFSTATE_LOCK_TABLE` with your bucket and table names.

3. **Initialize and apply Terraform:**

```bash
cd terraform
terraform init
terraform plan -out=tfplan
terraform apply tfplan
```

This provisions:
- VPC with public/private subnets
- EKS cluster (1.27) with managed node groups
- ECR repository
- Application Load Balancer (ALB)
- GitHub Actions OIDC role for CI/CD

### GitHub Actions Setup

1. **Get Terraform outputs:**

```bash
terraform output github_oidc_role_arn
terraform output cluster_name
```

2. **Set GitHub repository secrets:**

Go to repository **Settings → Secrets and variables → Actions** and create:

| Secret Name | Value |
|---|---|
| `GITHUB_OIDC_ROLE` | ARN output from `github_oidc_role_arn` |
| `AWS_REGION` | Your AWS region (e.g., `us-east-1`) |
| `AWS_ACCOUNT_ID` | Your AWS account ID |
| `EKS_CLUSTER_NAME` | Output from `cluster_name` |

3. **Workflows:**

- **CI - test, build and push** (`.github/workflows/ci-build-and-push.yaml`):
  - Runs on every pull request and push to `main`
  - Runs unit tests
  - Builds Docker image and pushes to ECR

- **Deploy to EKS** (`.github/workflows/deploy.yaml`):
  - Runs on push to `main` after tests pass
  - Updates kubeconfig
  - Deploys via Helm to EKS

- **Terraform CI** (`.github/workflows/terraform.yml`):
  - Runs `terraform plan` on PRs modifying `terraform/`
  - Manual `terraform apply` via workflow dispatch or automatic on push to `main`

### Helm Deployment

The deployment is managed via Helm. Customize in `helm/values.yaml`:

```yaml
replicaCount: 3
image:
  repository: "ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com/health-api-service"
  tag: "latest"
service:
  type: LoadBalancer
  port: 8000
```

GitHub Actions automatically sets the correct image URI during deployment.

### Optional: Enable HTTPS with ACM

```bash
terraform apply -var="enable_https=true" -var="acm_certificate_arn=arn:aws:acm:..."
```

Or configure Route53 DNS:

```bash
terraform apply -var="domain_name=api.example.com" -var="route53_zone_id=Z..."
```

### Monitoring & Access

After deployment:

```bash
# Get ALB DNS name
terraform output alb_dns_name

# Check pod status
kubectl get pods -n default

# View logs
kubectl logs -n default deployment/health

# Port-forward for local testing
kubectl port-forward -n default svc/health 8000:8000
curl http://localhost:8000/health
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
