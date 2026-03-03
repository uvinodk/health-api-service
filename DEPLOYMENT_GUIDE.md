# Health API Service - Deployment Guide

This guide walks you through deploying the Health API Service to AWS App Runner using Terraform and GitHub Actions CI/CD.

## Architecture Overview

- **App Runner**: Containerized application platform (cheap, simple)
- **ECR**: Stores Docker images built by GitHub Actions
- **GitHub Actions**: Automated CI/CD (test, build, push, deploy)
- **Terraform**: Infrastructure-as-Code for all AWS resources
- **S3 + DynamoDB**: Remote state backend for Terraform

## Prerequisites

- AWS account with appropriate IAM permissions
- Terraform >= 1.3 (if running locally)
- Docker (for building images locally, optional)
- Optional: GitHub CLI (`gh`) for setting secrets from terminal

## Step 1: Set Up Terraform State Backend (One-Time)

Create an S3 bucket and DynamoDB table to store Terraform state:

```bash
export AWS_REGION=us-west-1
export ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Create S3 bucket
aws s3 mb s3://health-api-tfstate-${ACCOUNT_ID} --region ${AWS_REGION}

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket health-api-tfstate-${ACCOUNT_ID} \
  --versioning-configuration Status=Enabled

# Create DynamoDB table for state locking
aws dynamodb create-table \
  --table-name health-api-tfstate-lock \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
  --region ${AWS_REGION}
```

## Step 2: Update Terraform Backend Configuration

Edit `terraform/provider.tf` and replace placeholders:

```hcl
backend "s3" {
  bucket         = "health-api-tfstate-REPLACE_WITH_ACCOUNT_ID"
  key            = "health-api-service/terraform.tfstate"
  region         = "us-west-1"  # or your preferred region
  dynamodb_table = "health-api-tfstate-lock"
  encrypt        = true
}
```

## Step 3: Provision AWS Infrastructure

Initialize Terraform and apply the configuration:

```bash
cd terraform

# Download provider plugins and initialize backend
terraform init

# Preview changes
terraform plan -out=tfplan

# Apply changes (takes ~10-15 minutes for EKS+VPC if enabled)
terraform apply tfplan
```

Capture the outputs:

```bash
# Get the GitHub OIDC role ARN
terraform output github_oidc_role_arn

# Get App Runner service URL (after deployment)
terraform output apprunner_service_url

# Get ALB DNS name (if using EKS)
terraform output alb_dns_name
```

## Step 4: Set GitHub Repository Secrets

Set the following secrets in your GitHub repository (Settings → Secrets and variables → Actions):

### Required Secrets

| Secret Name | Value | Example |
|---|---|---|
| `GITHUB_OIDC_ROLE` | ARN from `terraform output github_oidc_role_arn` | `arn:aws:iam::123456789012:role/github-actions-health-api-role` |
| `AWS_REGION` | Your AWS region | `us-west-1` |
| `AWS_ACCOUNT_ID` | Your AWS account ID | `123456789012` |

### Optional Secrets (only if switching to EKS)

| Secret Name | Value |
|---|---|
| `EKS_CLUSTER_NAME` | `health-api-cluster` |

**Option A: Using GitHub CLI (if installed)**

```bash
gh secret set GITHUB_OIDC_ROLE --body "arn:aws:iam::123456789012:role/github-actions-health-api-role"
gh secret set AWS_REGION --body "us-west-1"
gh secret set AWS_ACCOUNT_ID --body "123456789012"
```

**Option B: Using GitHub Web UI**

1. Go to repository → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add each secret from the table above

## Step 5: Trigger the Deployment

### Option A: Push to main branch

The deployment is triggered automatically when you merge the PR to `main`:

```bash
# Or merge the PR via GitHub web UI
git checkout main
git pull origin main
```

This triggers:
1. CI workflow → runs tests, builds Docker image, pushes to ECR
2. Deploy workflow → runs `terraform apply` with the image tag, deploys to App Runner

### Option B: Manual Trigger (for testing)

```bash
gh workflow run terraform.yml --ref feat/app-runner-automation
```

## Step 6: Monitor the Deployment

### Watch GitHub Actions

1. Go to repository → Actions
2. Monitor the running workflows:
   - `CI - test, build and push` - builds and pushes image
   - `Deploy to App Runner (Terraform)` - deploys to AWS

### Check App Runner Status

```bash
# Get service status
aws apprunner describe-service \
  --service-arn "arn:aws:apprunner:us-west-1:ACCOUNT_ID:service/health-api-apprunner/XXXXX" \
  --region us-west-1

# Get service URL
terraform output apprunner_service_url

# Test the endpoint
curl https://YOUR_SERVICE_URL/health
```

### View Application Logs

```bash
aws apprunner describe-service-logs \
  --service-arn "arn:aws:apprunner:us-west-1:ACCOUNT_ID:service/health-api-apprunner/XXXXX" \
  --region us-west-1
```

## Step 7: Access the Application

Once deployed, the health endpoint is available at:

```
https://YOUR_SERVICE_URL/health
```

Example response:

```json
{
  "status": "Healthy",
  "timestamp": "2026-03-03T12:34:56Z",
  "uptime": {
    "seconds": 123.45,
    "human_readable": "2m 3s"
  },
  "system": {
    "cpu_usage_percent": 12.5,
    "memory": {
      "used_percent": 45.2,
      "available_gb": 1.23
    },
    "disk": {
      "used_percent": 5.8,
      "free_gb": 234.56
    }
  }
}
```

## Cleanup / Teardown

To delete all AWS resources (and stop charges):

```bash
cd terraform

# Destroy all resources (requires confirmation)
terraform destroy

# Or with auto-approve (careful!)
terraform destroy -auto-approve
```

You can also filter resources to delete by tags in the AWS Console:
- `Project: health-api-service`
- `Owner: uvinodk`
- `Environment: prod`

## Troubleshooting

### "Input required and not supplied: aws-region"

**Cause**: `AWS_REGION` secret is not set.
**Fix**: Set the secret in GitHub → Settings → Secrets and variables → Actions.

### Terraform init fails

**Cause**: S3 bucket or DynamoDB table doesn't exist or credentials are wrong.
**Fix**:
```bash
# Verify S3 bucket exists
aws s3 ls s3://health-api-tfstate-ACCOUNT_ID

# Check local AWS credentials
aws sts get-caller-identity
```

### App Runner deployment fails

**Cause**: IAM role doesn't have permission or image not in ECR.
**Fix**:
```bash
# Check App Runner logs
aws apprunner describe-service-logs --service-arn ARN

# Verify image in ECR
aws ecr list-images --repository-name health-api-service --region us-west-1

# Check GitHub Actions workflow logs in repo → Actions
```

### Can't connect to deployed service

**Cause**: Service might still be starting or endpoint URL is wrong.
**Fix**:
```bash
# Get the correct URL
terraform output apprunner_service_url

# Wait a couple minutes for service to start, then test
curl https://YOUR_SERVICE_URL/health
```

## Environment Variables

You can customize Terraform variables:

```bash
# Deploy with custom region
terraform apply -var="aws_region=us-east-1"

# Switch to EKS instead of App Runner
terraform apply -var="use_apprunner=false"

# Custom project/owner tags
terraform apply -var="project_name=my-project" -var="owner=my-team"
```

## Next Steps

1. **Add custom domain** → Edit `terraform/route53_acm_vars.tf` and run `terraform apply -var="domain_name=api.example.com" -var="route53_zone_id=Z..."`
2. **Enable HTTPS** → Request ACM certificate, then apply with `-var="enable_https=true" -var="acm_certificate_arn=arn:aws:acm:..."`
3. **Scale up** → Increase `desired_capacity` in `terraform/variables.tf`
4. **Monitor** → Set up CloudWatch alarms or integrate with monitoring tools

## Reference

- [AWS App Runner docs](https://docs.aws.amazon.com/apprunner/)
- [Terraform AWS provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [GitHub Actions OIDC](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect)
