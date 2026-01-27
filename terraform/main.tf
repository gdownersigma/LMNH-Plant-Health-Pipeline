provider "aws" {
  region = var.AWS_REGION
  access_key = var.AWS_ACCESS_KEY
  secret_key = var.AWS_SECRET_KEY
}

# Existing Resources

# VPC
data "aws_vpc" "c21-vpc" {
    id = var.VPC_ID
}

## public subnets
data "aws_subnet" "c21-public-subnet-a" {
  id = var.SUBNET_ID_A
}

data "aws_subnet" "c21-public-subnet-b" {
  id = var.SUBNET_ID_B
}

data "aws_subnet" "c21-public-subnet-c" {
  id = var.SUBNET_ID_C
}


# S3 Bucket

# Create new bucket
resource "aws_s3_bucket" "plant-storage" {
    bucket = "c21-curdie-plant-storage"
    
    tags = {
        Name = "C21 Curdie Plant Storage Bucket"
        Environment = "Dev"
    }
}

# Access existing bucket
# data "aws_s3_bucket" "plant-storage" {
#     bucket = "c21-curdie-plant-storage"
# }

