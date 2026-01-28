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