provider "aws" {
  region = var.DEFAULT_REGION
  access_key = var.ACCESS_KEY_ID
  secret_key = var.SECRET_ACCESS_KEY
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

# Lambda Images
data "aws_ecr_image" "first-pipeline-image" {
    repository_name = "${var.BASE_NAME}-live-pipeline"
    image_tag       = "latest"
}

data "aws_ecr_image" "second-pipeline-image" {
    repository_name = "${var.BASE_NAME}-rds-to-s3-pipeline"
    image_tag       = "latest"
}

## Shared Lambda IAM Role and Permissions
data "aws_iam_policy_document" "lambda-trust-policy" {
    statement {
        effect = "Allow"
        principals {
            type        = "Service"
            identifiers = ["lambda.amazonaws.com"]
        }
        actions = ["sts:AssumeRole"]
    }
}

data "aws_iam_policy_document" "lambda-permissions-policy" {
    statement {
        effect = "Allow"
        resources = ["arn:aws:logs:*:*:*"]
        actions = [
            "logs:CreateLogGroup",
            "logs:CreateLogStream",
            "logs:PutLogEvents"
        ]
    }
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
}

resource "aws_iam_role" "pipeline-lambda-role" {
    name               = "${var.BASE_NAME}-pipeline-lambda-role"
    assume_role_policy = data.aws_iam_policy_document.lambda-trust-policy.json
}

resource "aws_iam_role_policy" "pipeline-lambda-permissions" {
    name   = "${var.BASE_NAME}-pipeline-lambda-policy"
    role   = aws_iam_role.pipeline-lambda-role.id
    policy = data.aws_iam_policy_document.lambda-permissions-policy.json
}

## First Pipeline Lambda - Every Minute Pipeline
resource "aws_lambda_function" "first-pipeline" {
    function_name = "${var.BASE_NAME}-first-pipeline"
    role          = aws_iam_role.pipeline-lambda-role.arn
    memory_size   = 512
    timeout = 60

    package_type = "Image"
    image_uri    = data.aws_ecr_image.first-pipeline-image.image_uri

    environment {
        variables = {
            DB_HOST   = var.DB_HOST
            DB_NAME   = var.DB_NAME
            DB_USER   = var.DB_USER
            DB_PASSWORD   = var.DB_PASSWORD
            DB_SCHEMA   = var.DB_SCHEMA
            DB_PORT   = var.DB_PORT
        }
    }

    tags = {
        Name = "${var.BASE_NAME} Minutely Lambda"
    }
}

## Second Pipeline Lambda - Daily Pipeline
resource "aws_lambda_function" "second-pipeline" {
    function_name = "${var.BASE_NAME}-second-pipeline"
    role          = aws_iam_role.pipeline-lambda-role.arn
    memory_size   = 512
    timeout = 60
    package_type = "Image"
    image_uri    = data.aws_ecr_image.second-pipeline-image.image_uri

    environment {
        variables = {
            S3_BUCKET_NAME = aws_s3_bucket.plant-storage.bucket
            DB_HOST   = var.DB_HOST
            DB_NAME   = var.DB_NAME
            DB_USER   = var.DB_USER
            DB_PASSWORD   = var.DB_PASSWORD
            DB_PORT   = var.DB_PORT
            ACCESS_KEY_ID = var.ACCESS_KEY_ID
            SECRET_ACCESS_KEY = var.SECRET_ACCESS_KEY
            DEFAULT_REGION = var.DEFAULT_REGION
        }
    }

    tags = {
        Name = "${var.BASE_NAME} Daily Lambda"
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
        resources = [
            aws_lambda_function.first-pipeline.arn,
            aws_lambda_function.second-pipeline.arn
        ]
        actions = ["lambda:InvokeFunction"]
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



# First Pipeline EventBridge Schedule (every minute)
resource "aws_scheduler_schedule" "first-pipeline-schedule" {
    name = "${var.BASE_NAME}-first-pipeline-schedule"
    flexible_time_window {
      mode = "OFF"
    }
    schedule_expression = "cron(* * * * ? *)"
    schedule_expression_timezone = "Europe/London"

    target {
        arn = aws_lambda_function.first-pipeline.arn
        role_arn = aws_iam_role.schedule-role.arn
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

# Second Pipeline EventBridge Schedule (11:55 PM daily)
resource "aws_scheduler_schedule" "second-pipeline-schedule" {
    name = "${var.BASE_NAME}-second-pipeline-schedule"
    flexible_time_window {
      mode = "OFF"
    }
    schedule_expression = "cron(55 23 * * ? *)"
    schedule_expression_timezone = "Europe/London"

    target {
        arn = aws_lambda_function.second-pipeline.arn
        role_arn = aws_iam_role.schedule-role.arn
    }
}

# Dashboard ECS service

## Dashboard image

data "aws_ecr_image" "dashboard-image" {
    repository_name = "${var.BASE_NAME}-plant-dashboard"
    image_tag       = "latest"
}

# ECS execution role

resource "aws_iam_role" "ecs_task_execution" {
  name = "${var.BASE_NAME}-task-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution" {
  role       = aws_iam_role.ecs_task_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# ECS Security Group

resource "aws_security_group" "ecs_tasks" {
  name        = "${var.BASE_NAME}-ecs-tasks-sg"
  description = "Security group for ECS tasks"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "Streamlit port"
    from_port   = 8501
    to_port     = 8501
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# ECS Log Group

resource "aws_cloudwatch_log_group" "ecs_dashboard_logs" {
  name              = "/ecs/${var.BASE_NAME}-dashboard"
  retention_in_days = 7
}

# ECS Task Definition

resource "aws_ecs_task_definition" "streamlit" {
  family                   = "${var.BASE_NAME}-streamlit-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 512
  memory                   = 1024
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn

  container_definitions = jsonencode([
    {
      name  = "${var.BASE_NAME}-streamlit"
      image = data.aws_ecr_image.dashboard-image.image_uri

      portMappings = [
        {
          containerPort = 8501
          hostPort      = 8501
          protocol      = "tcp"
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.ecs_dashboard_logs.name
          "awslogs-region"        = var.DEFAULT_REGION
          "awslogs-stream-prefix" = "ecs"
        }
      }

      essential = true
    }
  ])
}
