"""Load plant data into the database."""
# pylint: disable=redefined-outer-name
from os import environ as ENV
import pandas as pd
from dotenv import load_dotenv
from pymssql import connect


def nan_to_none(value):
    """Convert pandas NaN to Python None for SQL compatibility."""
    if pd.isna(value):
        return None
    return value


def get_connection():
    """Create a connection to the MS SQL database."""
    load_dotenv()
    return connect(
        server=ENV["DB_HOST"],
        user=ENV["DB_USER"],
        password=ENV["DB_PASSWORD"],
        database=ENV["DB_NAME"],
        port=ENV.get("DB_PORT", 1433)
    )


def get_origin_id(conn, lat: float, long: float) -> int | None:
    """Get origin_id from database by lat/long, return None if not found."""
    query = "SELECT origin_id FROM origin WHERE lat = %s AND long = %s"
    with conn.cursor() as cursor:
        cursor.execute(query, (float(lat), float(long)))
        result = cursor.fetchone()
        return result[0] if result else None


def get_origin_id_by_city(conn, city_name: str, lat: float, long: float) -> int | None:
    """Get origin_id from database by city name and approximate coordinates."""
    query = """
        SELECT o.origin_id FROM origin o
        JOIN city c ON o.city_id = c.city_id
        WHERE c.city_name = %s
    """
    with conn.cursor() as cursor:
        cursor.execute(query, (city_name,))
        result = cursor.fetchone()
        return result[0] if result else None


def get_plant_by_id(conn, plant_id: int) -> dict | None:
    """Get plant record from database by plant_id."""
    query = "SELECT plant_id FROM plant WHERE plant_id = %s"
    with conn.cursor() as cursor:
        cursor.execute(query, (plant_id,))
        result = cursor.fetchone()
        return result[0] if result else None


def create_plant(conn, plant_id: int, name: str, scientific_name: str,
                 origin_id: int, botanist_id: int,
                 image_license_url: str, image_url: str, thumbnail: str) -> int:
    """Create a new plant record and return the plant_id."""
    with conn.cursor() as cursor:
        cursor.execute(
            """INSERT INTO plant 
               (plant_id, name, scientific_name, origin_id, botanist_id, 
                image_license_url, image_url, thumbnail) 
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (plant_id, name, scientific_name, origin_id, botanist_id,
             image_license_url, image_url, thumbnail)
        )
        return plant_id


def update_plant(conn, plant_id: int, name: str, scientific_name: str,
                 origin_id: int, botanist_id: int,
                 image_license_url: str, image_url: str, thumbnail: str) -> int:
    """Update an existing plant record."""
    with conn.cursor() as cursor:
        cursor.execute(
            """UPDATE plant 
               SET name = %s, scientific_name = %s, origin_id = %s, 
                   botanist_id = %s, image_license_url = %s, 
                   image_url = %s, thumbnail = %s
               WHERE plant_id = %s""",
            (name, scientific_name, origin_id, botanist_id,
             image_license_url, image_url, thumbnail, plant_id)
        )
        return plant_id


def load_plant(conn, row: dict, botanist_id: int, origin_id: int) -> int:
    """Load a single plant row into the database."""
    existing = get_plant_by_id(conn, row["plant_id"])

    # Convert NaN values to None for SQL compatibility
    scientific_name = nan_to_none(row.get("scientific_name"))
    image_license_url = nan_to_none(row.get("image_license_url"))
    image_original_url = nan_to_none(row.get("image_original_url"))
    image_thumbnail = nan_to_none(row.get("image_thumbnail"))

    if existing:
        return update_plant(
            conn,
            row["plant_id"],
            row["name"],
            scientific_name,
            origin_id,
            botanist_id,
            image_license_url,
            image_original_url,
            image_thumbnail
        )
    else:
        return create_plant(
            conn,
            row["plant_id"],
            row["name"],
            scientific_name,
            origin_id,
            botanist_id,
            image_license_url,
            image_original_url,
            image_thumbnail
        )


def load_plants(df: pd.DataFrame, botanist_email_to_id: dict) -> None:
    """Load all plants from dataframe into database.

    Args:
        df: DataFrame with plant data
        botanist_email_to_id: dict mapping botanist_email -> botanist_id
    """
    conn = get_connection()

    try:
        for _, row in df.iterrows():
            botanist_id = botanist_email_to_id.get(row["botanist_email"])

            # Look up origin_id directly from DB using coordinates
            origin_id = get_origin_id(
                conn,
                row["origin_latitude"],
                row["origin_longitude"]
            )

            if botanist_id is None:
                print(f"Warning: No botanist_id for {row['botanist_email']}")
                continue
            if origin_id is None:
                print(
                    f"Warning: No origin_id for ({row['origin_latitude']}, {row['origin_longitude']})")
                continue

            load_plant(conn, row, botanist_id, origin_id)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


if __name__ == "__main__":
    conn = get_connection()
    query = "SELECT * FROM plant"
    print(pd.read_sql(query, conn))
    conn.close()
