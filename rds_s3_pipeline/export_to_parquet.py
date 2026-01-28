import os
import re
import pymssql
import pandas as pd
import boto3
import awswrangler as wr
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Create boto3 session with explicit credentials
session = boto3.Session(
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_DEFAULT_REGION', 'eu-west-2')
)

def read_table_to_dataframe(cursor, table_name):
    """Read entire table into a pandas DataFrame"""
    cursor.execute(f"SELECT * FROM {table_name}")
    columns = [desc[0] for desc in cursor.description]
    data = cursor.fetchall()
    return pd.DataFrame(data, columns=columns)

def write_partitioned_parquet(df, table_name, base_path='s3://input/'):
    """Write DataFrame to parquet files (time-partitioned for plant_reading only)"""
    output_path = f"{base_path}/{table_name}"

    if table_name == 'plant_reading' and 'recording_taken' in df.columns:
        # Partition by recording_taken for plant_reading table
        df['recording_taken'] = pd.to_datetime(df['recording_taken'])

        # Add partition columns
        df['year'] = df['recording_taken'].dt.year
        df['month'] = df['recording_taken'].dt.month.apply(lambda x: f"{x:02d}")
        df['day'] = df['recording_taken'].dt.day.apply(lambda x: f"{x:02d}")
        df['hour'] = df['recording_taken'].dt.hour.apply(lambda x: f"{x:02d}")
        df['minute'] = df['recording_taken'].dt.minute.apply(lambda x: f"{x:02d}")

        # Write with time partitioning
        wr.s3.to_parquet(
            df=df,
            path=output_path,
            dataset=True,
            partition_cols=['year', 'month', 'day', 'hour', 'minute'],
            mode='overwrite',
            boto3_session=session
        )
    else:
        # Write other tables as simple parquet files without time partitions
        wr.s3.to_parquet(
            df=df,
            path=f"{output_path}/data.parquet",
            boto3_session=session
        )

    print(f"✓ Exported {table_name} ({len(df)} rows)")

def export_all_tables():
    """Main function to export all tables to partitioned parquet files"""
    # Connect to database
    conn = pymssql.connect(
        server=os.getenv('DB_HOST'),
        port=int(os.getenv('DB_PORT', 1433)),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )
    cursor = conn.cursor()

    # Get all tables from schema
    tables = ['plant_reading', 'plant', 'origin', 'country', 'city', 'botanist']
    print(f"Extracting {len(tables)} tables: {', '.join(tables)}\n")

    # S3 base path with bucket name from environment
    s3_bucket = os.getenv('S3_BUCKET_NAME')
    if not s3_bucket:
        raise Exception("No s3 bucket name found in environment!")

    base_path = f"s3://{s3_bucket}/input"
    print(f"Output path: {base_path}\n")

    # Create empty output folder at bucket root if it doesn't exist
    output_folder_path = f"s3://{s3_bucket}/output/"
    wr.s3.to_parquet(
        df=pd.DataFrame({'_placeholder': []}),
        path=f"{output_folder_path}.placeholder",
        boto3_session=session
    )
    print(f"✓ Ensured output folder exists: {output_folder_path}\n")

    # Export each table
    for table in tables:
        try:
            df = read_table_to_dataframe(cursor, table)
            if not df.empty:
                write_partitioned_parquet(df, table, base_path=base_path)
            else:
                print(f"⚠ Skipped {table} (empty table)")
        except Exception as e:
            print(f"✗ Error exporting {table}: {e}")

    cursor.close()
    conn.close()
    print("\n✓ Export complete!")

if __name__ == "__main__":
    export_all_tables()
