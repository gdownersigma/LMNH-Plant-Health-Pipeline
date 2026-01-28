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
        resources = ["${var.TASK_DEFINITION_ARN}:*",
                      var.TASK_DEFINITION_ARN]
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

# IAM Role and Policy for Scheduler
resource "aws_iam_role" "schedule-role" {
    name               = "${var.BASE_NAME}-scheduler-etl-role"
    assume_role_policy = data.aws_iam_policy_document.schedule-trust-policy.json
}

resource "aws_iam_role_policy" "schedule-permissions" {
    name   = "${var.BASE_NAME}-execution-policy"
    role   = aws_iam_role.schedule-role.id
    policy = data.aws_iam_policy_document.schedule-permissions-policy.json
}

# Security Group for ETL Tasks
resource "aws_security_group" "etl-sg" {
    name        = "${var.BASE_NAME}-etl-sg"
    description = "Security group for ETL tasks"
    vpc_id      = data.aws_vpc.c21-vpc.id

    egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
}
}

# ETL Eventbridge Schedule
resource "aws_scheduler_schedule" "data-upload-schedule" {
    name = "${var.BASE_NAME}-etl-schedule"
    flexible_time_window {
      mode = "OFF"
    }
    schedule_expression = "cron(* * * * ? *)"
    schedule_expression_timezone = "Europe/London"

    target {
        arn = data.aws_ecs_cluster.target-cluster.arn
        role_arn = aws_iam_role.schedule-role.arn
        ecs_parameters {
            task_definition_arn = var.TASK_DEFINITION_ARN
            launch_type = "FARGATE"
            network_configuration {
                subnets          = [data.aws_subnet.c21-public-subnet-a.id,
                                    data.aws_subnet.c21-public-subnet-b.id,
                                    data.aws_subnet.c21-public-subnet-c.id]
                security_groups  = [aws_security_group.etl-sg.id]
                assign_public_ip = true
            }
        }
    }
}

# CloudWatch Log Group for ETL Task Logs
resource "aws_cloudwatch_log_group" "etl-logs" {
    name              = "/ecs/${var.BASE_NAME}-etl-task"
    retention_in_days = 7

    tags = {
        Name = "${var.BASE_NAME} ETL Task Logs"
    }
}

# Glue Crawler IAM Role
data "aws_iam_policy_document" "glue-trust-policy" {
    statement {
        effect = "Allow"
        principals {
            type        = "Service"
            identifiers = ["glue.amazonaws.com"]
        }
        actions = ["sts:AssumeRole"]
    }
}

data "aws_iam_policy_document" "glue-permissions-policy" {
    statement {
        effect = "Allow"
        resources = [
            aws_s3_bucket.plant-storage.arn,
            "${aws_s3_bucket.plant-storage.arn}/*"
        ]
        actions = [
            "s3:GetObject",
            "s3:PutObject",
            "s3:ListBucket"
        ]
    }

    statement {
        effect    = "Allow"
        resources = ["*"]
        actions = [
            "glue:*",
            "logs:CreateLogGroup",
            "logs:CreateLogStream",
            "logs:PutLogEvents"
        ]
    }
}

resource "aws_iam_role" "glue-crawler-role" {
    name               = "${var.BASE_NAME}-glue-crawler-role"
    assume_role_policy = data.aws_iam_policy_document.glue-trust-policy.json
}

resource "aws_iam_role_policy" "glue-crawler-permissions" {
    name   = "${var.BASE_NAME}-glue-crawler-policy"
    role   = aws_iam_role.glue-crawler-role.id
    policy = data.aws_iam_policy_document.glue-permissions-policy.json
}

resource "aws_iam_role_policy_attachment" "glue-service-role" {
    role       = aws_iam_role.glue-crawler-role.name
    policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
}

# Glue Catalog Database
resource "aws_glue_catalog_database" "plant-catalog-db" {
    name = replace("${var.BASE_NAME}_plant_catalog", "-", "_")

    description = "Glue catalog database for plant health data"
}

# Glue Crawler
resource "aws_glue_crawler" "plant-data-crawler" {
    name          = "${var.BASE_NAME}-plant-crawler"
    role          = aws_iam_role.glue-crawler-role.arn
    database_name = aws_glue_catalog_database.plant-catalog-db.name

    s3_target {
        path = "s3://${aws_s3_bucket.plant-storage.bucket}"
    }

    schedule = "cron(0 0 * * ? *)"

    schema_change_policy {
        delete_behavior = "LOG"
        update_behavior = "UPDATE_IN_DATABASE"
    }

    tags = {
        Name = "${var.BASE_NAME} Plant Data Crawler"
    }
}

