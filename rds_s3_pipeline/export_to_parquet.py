import os
import pymssql
import pandas as pd
import boto3
import awswrangler as wr
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def create_boto3_session():
    """Create and return boto3 session with credentials from environment"""
    return boto3.Session(
        aws_access_key_id=os.getenv('ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('SECRET_ACCESS_KEY'),
        region_name=os.getenv('DEFAULT_REGION', 'eu-west-2')
    )

def get_raw_data_query():
    """Return simple SQL query to get raw plant reading data with joins"""
    return """
        SELECT
            CAST(pr.recording_taken AS DATE) AS reading_date,
            p.plant_id,
            p.name AS plant_name,
            p.scientific_name,
            b.name AS botanist_name,
            b.email AS botanist_email,
            b.phone AS botanist_phone,
            pr.temperature,
            pr.soil_moisture,
            pr.last_watered
        FROM plant p
        INNER JOIN botanist b ON p.botanist_id = b.botanist_id
        INNER JOIN plant_reading pr ON p.plant_id = pr.plant_id
        ORDER BY pr.recording_taken DESC, p.plant_id
    """

def execute_query(connection, query):
    """Execute SQL query and return results as DataFrame"""
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        data = cursor.fetchall()
        return pd.DataFrame(data, columns=columns)
    finally:
        cursor.close()

def calculate_daily_summary(df) -> pd.DataFrame:
    """Calculate daily plant health summary statistics using pandas"""
    # Convert dates
    df['reading_date'] = pd.to_datetime(df['reading_date'])
    df['last_watered'] = pd.to_datetime(df['last_watered'])

    # Group by date and plant, calculate aggregations
    summary = df.groupby(
        ['reading_date', 'plant_id', 'plant_name', 'scientific_name',
         'botanist_name', 'botanist_email', 'botanist_phone'],
        as_index=False,
        dropna=False
    ).agg(
        min_temperature=('temperature', 'min'),
        max_temperature=('temperature', 'max'),
        avg_temperature=('temperature', 'mean'),
        median_temperature=('temperature', lambda x: x.quantile(0.5)),
        percentile_25_temperature=('temperature', lambda x: x.quantile(0.25)),
        percentile_75_temperature=('temperature', lambda x: x.quantile(0.75)),
        min_humidity=('soil_moisture', 'min'),
        max_humidity=('soil_moisture', 'max'),
        avg_humidity=('soil_moisture', 'mean'),
        median_humidity=('soil_moisture', lambda x: x.quantile(0.5)),
        percentile_25_humidity=('soil_moisture', lambda x: x.quantile(0.25)),
        percentile_75_humidity=('soil_moisture', lambda x: x.quantile(0.75)),
        times_watered=('last_watered', lambda x: x.dt.date.nunique())
    )

    # Sort by date descending
    summary = summary.sort_values(['reading_date', 'plant_id'], ascending=[False, True])

    return summary

def add_partition_columns(df):
    """Add year, month, day partition columns to DataFrame"""
    df['reading_date'] = pd.to_datetime(df['reading_date'])
    df['year'] = df['reading_date'].dt.year
    df['month'] = df['reading_date'].dt.month.apply(lambda x: f"{x:02d}")
    df['day'] = df['reading_date'].dt.day.apply(lambda x: f"{x:02d}")
    return df

def write_to_s3(df, output_path, partition_cols, session):
    """Write DataFrame to S3 as partitioned parquet"""
    wr.s3.to_parquet(
        df=df,
        path=output_path,
        dataset=True,
        partition_cols=partition_cols,
        filename_prefix='plant-health-daily-summary',
        mode='overwrite',
        boto3_session=session
    )

def create_output_folder(s3_bucket, session):
    """Create empty output folder in S3 bucket"""
    output_folder_path = f"s3://{s3_bucket}/output/"
    wr.s3.to_parquet(
        df=pd.DataFrame({'_placeholder': []}),
        path=f"{output_folder_path}.placeholder",
        boto3_session=session
    )
    return output_folder_path

def get_s3_bucket():
    """Get S3 bucket name from environment"""
    s3_bucket = os.getenv('S3_BUCKET_NAME')
    if not s3_bucket:
        raise Exception("No s3 bucket name found in environment!")
    return s3_bucket

def get_db_connection():
    """Create and return a database connection"""
    return pymssql.connect(
        server=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT', 1433),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )

def export_daily_summaries():
    """Main function to export daily plant summaries to S3"""
    print("[INFO] Starting daily plant summary export from RDS to S3...")

    # Setup
    session = create_boto3_session()
    conn = get_db_connection()
    s3_bucket = get_s3_bucket()
    base_path = f"s3://{s3_bucket}/input"

    print(f"Output path: {base_path}\n")

    # Create output folder
    output_folder = create_output_folder(s3_bucket, session)
    print(f"✓ Ensured output folder exists: {output_folder}\n")

    # Get raw data
    query = get_raw_data_query()
    raw_df = execute_query(conn, query)
    print(f"✓ Retrieved {len(raw_df)} raw plant reading records")

    if not raw_df.empty:
        # Calculate summary statistics with pandas
        summary_df = calculate_daily_summary(raw_df)
        print(f"✓ Calculated {len(summary_df)} daily plant summary records")

        # Transform and write
        summary_df = add_partition_columns(summary_df)
        output_path = f"{base_path}/daily_plant_summaries"
        write_to_s3(summary_df, output_path, ['year', 'month', 'day'], session)
        print(f"✓ Exported daily plant summaries ({len(summary_df)} rows) to {output_path}")
    else:
        print("⚠ No data to export")

    # Cleanup
    conn.close()
    print("\n✓ Export complete!")

def delete_old_plant_readings():
    """Delete plant_reading records older than 24 hours from the database"""
    print("\n[INFO] Starting deletion of old plant_reading records...")

    delete_query = """
        DELETE FROM plant_reading
        WHERE recording_taken < DATEADD(hour, -24, GETDATE())
    """

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(delete_query)
    deleted_count = cursor.rowcount
    conn.commit()
    cursor.close()
    conn.close()

    print(f"[INFO] Deleted {deleted_count} plant_reading records older than 24 hours.")

def handler(event, context):
    """Lambda handler function"""
    print("[INFO] Starting daily plant summary export from RDS to S3...")
    export_daily_summaries()
    print("[INFO] Export complete. Proceeding to delete old plant_reading records...")
    delete_old_plant_readings()
    print("[INFO] Data export and cleanup finished.")

if __name__ == "__main__":
    export_daily_summaries()
    delete_old_plant_readings()
