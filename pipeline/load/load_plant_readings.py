"""Load plant readings into the database."""
import pandas as pd
from os import environ as ENV
from dotenv import load_dotenv
import pymssql


def get_connection():
    """Create a connection to the MS SQL database."""
    load_dotenv()
    return pymssql.connect(
        server=ENV["DB_HOST"],
        user=ENV["DB_USER"],
        password=ENV["DB_PASSWORD"],
        database=ENV["DB_NAME"],
        port=ENV.get("DB_PORT", 1433)
    )


def load_csv(filepath: str) -> pd.DataFrame:
    """Load plant readings from CSV."""
    return pd.read_csv(filepath)


def insert_plant_reading(conn, row: dict) -> None:
    """Insert a single plant reading into the database."""
    query = """
        INSERT INTO plant_reading (plant_id, soil_moisture, temperature, recording_taken, last_watered)
        VALUES (%s, %s, %s, %s, %s)
    """
    with conn.cursor() as cursor:
        cursor.execute(query, (
            row["plant_id"],
            row["soil_moisture"],
            row["temperature"],
            row["recording_taken"],
            row["last_watered"]
        ))


def load_plant_readings(filepath: str) -> None:
    """Load all plant readings from CSV into the database."""
    df = load_csv(filepath)
    conn = get_connection()

    try:
        for _, row in df.iterrows():
            insert_plant_reading(conn, row)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


if __name__ == "__main__":
    load_plant_readings("plant_readings.csv")
