"""Load origin data into the database."""
import pandas as pd
from os import environ as ENV
from dotenv import load_dotenv
from pymssql import connect


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


def get_country_id(conn, country_name: str) -> int | None:
    """Get country ID from the database, return None if not found."""
    query = "SELECT country_id FROM country WHERE country_name = %s"
    with conn.cursor() as cursor:
        cursor.execute(query, (country_name,))
        result = cursor.fetchone()
        return result[0] if result else None


def get_city_id(conn, city_name: str, country_id: int) -> int | None:
    """Get city_id from the database, return None if not found."""
    query = "SELECT city_id FROM city WHERE city_name = %s AND country_id = %s"
    with conn.cursor() as cursor:
        cursor.execute(query, (city_name, country_id))
        result = cursor.fetchone()
        return result[0] if result else None


def create_country(conn, country_name: str) -> int:
    """Create a new country and return the new country_id."""
    with conn.cursor() as cursor:
        cursor.execute(
            "INSERT INTO country (country_name) VALUES (%s)", (country_name,))
        cursor.execute("SELECT SCOPE_IDENTITY()")
        return cursor.fetchone()[0]


def create_city(conn, city_name: str, country_id: int) -> int:
    """Create a new city and return the new city_id."""
    with conn.cursor() as cursor:
        cursor.execute(
            "INSERT INTO city (city_name, country_id) VALUES (%s, %s)", (city_name, country_id))
        cursor.execute("SELECT SCOPE_IDENTITY()")
        return cursor.fetchone()[0]


def get_or_create_country(conn, country_name: str) -> int:
    """Get country_id from database, or create if doesn't exist."""
    country_id = get_country_id(conn, country_name)
    if country_id is None:
        country_id = create_country(conn, country_name)
    return country_id


def get_or_create_city(conn, city_name: str, country_id: int) -> int:
    """Get city_id from database, or create if doesn't exist."""
    city_id = get_city_id(conn, city_name, country_id)
    if city_id is None:
        city_id = create_city(conn, city_name, country_id)
    return city_id


def insert_origin(conn, city_id: int, lat: float, long: float) -> int:
    """Insert origin record and return the new origin_id."""
    with conn.cursor() as cursor:
        cursor.execute(
            "INSERT INTO origin (city_id, lat, long) VALUES (%s, %s, %s)",
            (city_id, lat, long)
        )
        cursor.execute("SELECT SCOPE_IDENTITY()")
        return cursor.fetchone()[0]


def load_origin(conn, row: dict) -> int:
    """Load a single origin row into the database."""
    country_id = get_or_create_country(conn, row["origin_country"])
    city_id = get_or_create_city(conn, row["origin_city"], country_id)
    origin_id = insert_origin(
        conn, city_id, row["origin_latitude"], row["origin_longitude"])
    return origin_id


def load_origins(df: pd.DataFrame) -> None:
    """Load all origins from dataframe into database."""
    conn = get_connection()

    try:
        for _, row in df.iterrows():
            load_origin(conn, row)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def get_all_from_table(conn, table_name: str) -> pd.DataFrame:
    """Pull all data from a table."""
    query = f"SELECT * FROM {table_name}"
    return pd.read_sql(query, conn)


if __name__ == "__main__":
    print(get_all_from_table(get_connection(), "origin"))
