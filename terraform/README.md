## Prerequisites

```bash
brew install terraform localstack/tap/localstack-cli
```

## Deploy

```bash
localstack start -d
cd terraform
terraform init
terraform apply
```

## Verify

```bash
terraform show
terraform output
```

## Destroy

```bash
terraform destroy
localstack stop
```