# How to Use Terraform to Set Up Cloud Infrastructure

Ensure you are in the `terraform/` directory before running the following commands.
```bash
cd terraform/
```

## Terraform Variables

Ensure you have a `terraform.tfvars` file in the `terraform/` directory with variables matching those defined in `variables.tf`.

Run this command to create the file if it does not exist.
```bash
touch terraform.tfvars
```

Example usage (replace the placeholders with your actual values):
```hcl
AWS_ACCESS_KEY = "{}"
AWS_SECRET_KEY = "{}"
AWS_REGION = "eu-west-2"
VPC_ID = "{}"
SUBNET_ID_A = "{}"
SUBNET_ID_B = "{}"
SUBNET_ID_C = "{}"
BASE_NAME = "curdie"
```

## Initialize Terraform

Use this to initialize the Terraform working directory.
```bash
terraform init
```

## Use Terraform Plan

Use this to create an execution plan.
```bash
terraform plan
```

Then apply the changes with terraform.
```bash
terraform apply
```