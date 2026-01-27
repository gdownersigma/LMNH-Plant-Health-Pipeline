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

# ECS Cluster
data "aws_ecs_cluster" "target-cluster" {
    cluster_name = var.CLUSTER_NAME
}

# S3 Bucket

# Create new bucket
resource "aws_s3_bucket" "plant-storage" {
    bucket = "${var.BASE_NAME}-plant-storage"
    tags = {
        Name = "${var.BASE_NAME} Plant Storage Bucket"
    }
}

# ETL Eventbridge Schedule

## Trust Policy
data  "aws_iam_policy_document" "schedule-trust-policy" {
    statement {
        effect = "Allow"
        principals {
            type        = "Service"
            identifiers = ["scheduler.amazonaws.com"]
        }
        actions = ["sts:AssumeRole"]
    }
}

## Permission Policy
data  "aws_iam_policy_document" "schedule-permissions-policy" {

    statement {
        effect = "Allow"
        #resources = ["${task definition arn for etl pipeline lambda}:*"]
        actions = ["ecs:RunTask"]
        condition {
            test     = "ArnLike"
            variable = "ecs:cluster"
            values   = [data.aws_ecs_cluster.target-cluster.arn]
        }
    }

    statement {
        effect = "Allow"
        resources = ["*"]
        actions = ["iam:PassRole"]
        condition {
            test     = "StringLike"
            variable = "iam:PassedToService"
            values   = ["ecs-tasks.amazonaws.com"]
        }
    }

    statement {
        effect = "Allow"
        resources = ["arn:aws:logs:*:*:*"]
        actions = [
            "logs:CreateLogStream",
            "logs:PutLogEvents",
            "logs:CreateLogGroup"
        ]
    }
}