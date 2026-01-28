# RDS to S3 Pipeline

Export database tables to S3 as time-partitioned Parquet files.

## Running export_to_parquet.py

### Prerequisites
- Python 3.x
- Required packages: `pymssql`, `pandas`, `boto3`, `awswrangler`, `python-dotenv`
- `.env` file with database and AWS credentials

### Environment Variables

Ensure your `.env` file contains:
```env
# Database credentials
DB_HOST=your-db-host
DB_PORT=1433
DB_USER=your-username
DB_PASSWORD=your-password
DB_NAME=your-database

# AWS credentials
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_DEFAULT_REGION=eu-west-2
S3_BUCKET_NAME=your-bucket-name
```

### Run the Script

```bash
python export_to_parquet.py
```

The script will:
- Export all tables to S3
- Time-partition `plant_reading` table by `recording_taken` timestamp
- Save other tables as simple parquet files
- Create an `output/` folder in the S3 bucket

## Docker

### Build the Docker Image

```bash
docker buildx build --platform linux/amd64,linux/arm64 -t rds-s3-export .
```

## Output Structure

```
s3://your-bucket/
├── input/
│   ├── botanist/data.parquet
│   ├── plant/data.parquet
│   ├── city/data.parquet
│   ├── country/data.parquet
│   ├── origin/data.parquet
│   └── plant_reading/
│       └── year=2026/month=01/day=28/hour=14/minute=30/...
└── output/
```
