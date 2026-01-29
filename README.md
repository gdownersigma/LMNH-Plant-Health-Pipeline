# LMNH Plant Health Pipeline

Cloud-based ETL pipeline for processing and archiving live plant health data from the Liverpool Museum of Natural History.

## Architecture

![Architecture Diagram](./images/architecture_diagram.png)

**Two-stage pipeline system:**
1. **Short-term Pipeline (every minute)**: Extracts plant data from API → transforms → loads to Microsoft SQL Server RDS
2. **Long-term Pipeline (every 24 hours)**: Exports RDS data to S3 as time-partitioned Parquet files → deletes records older than 24 hours from RDS

## Quick Start

### Prerequisites
- Python 3.x
- Docker
- AWS CLI configured
- Microsoft SQL Server database

### 1. Clone and Setup

```bash
git clone https://github.com/gdownersigma/LMNH-Plant-Health-Pipeline.git
cd LMNH-Plant-Health-Pipeline
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 2. Configure Environment

Create a `.env` file in the project root:

```env
# Database
DB_HOST=your-db-host
DB_PORT=1433
DB_USER=your-username
DB_PASSWORD=your-password
DB_NAME=your-database

# AWS
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_DEFAULT_REGION=eu-west-2
S3_BUCKET_NAME=your-bucket-name
```

### 3. Initialize Database Schema

```bash
cd schema
pip install -r requirements.txt
python load_schema_and_data.py
```

## Running the Pipelines

### Short-term Pipeline (RDS Ingestion)

```bash
cd pipeline
pip install -r pipeline_requirements.txt
python pipeline.py
```

### Long-term Pipeline (RDS to S3 Archive)

```bash
cd rds_s3_pipeline
pip install -r requirements.txt
python export_to_parquet.py
```

## Docker Deployment

### Build and Push to AWS ECR

```bash
# Authenticate Docker to ECR
aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin {ACCOUNT_ID}.dkr.ecr.eu-west-2.amazonaws.com

# Create ECR repositories
aws ecr create-repository --repository-name lmnh-etl-pipeline --region eu-west-2
aws ecr create-repository --repository-name lmnh-rds-to-s3 --region eu-west-2

# Build and push ETL pipeline
cd pipeline
docker buildx build --platform linux/amd64 -t lmnh-etl-pipeline .
docker tag lmnh-etl-pipeline:latest {ACCOUNT_ID}.dkr.ecr.eu-west-2.amazonaws.com/lmnh-etl-pipeline:latest
docker push {ACCOUNT_ID}.dkr.ecr.eu-west-2.amazonaws.com/lmnh-etl-pipeline:latest

# Build and push RDS-to-S3 pipeline
cd ../rds_s3_pipeline
docker buildx build --platform linux/amd64 -t lmnh-rds-to-s3 .
docker tag lmnh-rds-to-s3:latest {ACCOUNT_ID}.dkr.ecr.eu-west-2.amazonaws.com/lmnh-rds-to-s3:latest
docker push {ACCOUNT_ID}.dkr.ecr.eu-west-2.amazonaws.com/lmnh-rds-to-s3:latest
```

## Infrastructure Deployment

Deploy AWS infrastructure using Terraform:

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

This creates:
- ECS Fargate tasks for both pipelines
- EventBridge schedules (1 min & 24 hour intervals)
- IAM roles and policies
- S3 bucket for long-term storage

## Project Structure

```
├── pipeline/              # Short-term ETL pipeline
│   ├── extract/          # API data extraction
│   ├── transform/        # Data cleaning & transformation
│   ├── load/             # RDS database loading
│   └── pipeline.py       # Main orchestration script
├── rds_s3_pipeline/      # Long-term archival pipeline
│   └── export_to_parquet.py  # RDS → S3 export & cleanup
├── schema/               # Database schema & seed data
│   ├── schema.sql        # Table definitions
│   ├── load_schema_and_data.py
│   └── dummy_tables/     # Sample data for testing
└── terraform/            # Infrastructure as Code
    ├── main.tf
    └── variables.tf
```

## S3 Output Structure

```
s3://your-bucket/
├── input/
│   ├── botanist/data.parquet
│   ├── plant/data.parquet
│   ├── city/data.parquet
│   ├── country/data.parquet
│   ├── origin/data.parquet
│   └── plant_reading/
│       └── year=2026/
│           └── month=01/
│               └── day=28/
│                   └── hour=14/
│                       └── minute=30/
│                           └── data.parquet
└── output/
```

## Key Features

- **Automated ETL**: Minute-by-minute plant data ingestion
- **Data Archival**: Time-partitioned Parquet files for efficient querying
- **Cost Optimization**: Automatic deletion of old RDS data to minimize storage costs
- **Scalable**: Containerized pipelines running on AWS ECS Fargate
- **Infrastructure as Code**: Fully reproducible AWS setup with Terraform

## Useful Commands

### Test Database Connection
```bash
python -c "import pymssql; pymssql.connect(server='your-host', user='user', password='pass', database='db')"
```

### Check S3 Data
```bash
aws s3 ls s3://your-bucket/input/plant_reading/ --recursive
```

### View Lambda Logs
```bash
aws logs tail /aws/lambda/your-function-name --follow
```

### Count Old RDS Records (>24h)
```sql
SELECT COUNT(*) FROM plant_reading WHERE recording_taken < DATEADD(hour, -24, GETDATE());
```