"""Load botanist data into the database."""
from os import environ as ENV
import pandas as pd
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


def get_botanist_id(conn, email: str) -> int | None:
    """Get botanist_id from database by email, return None if not found."""
    query = "SELECT botanist_id FROM botanist WHERE email = %s"
    with conn.cursor() as cursor:
        cursor.execute(query, (email,))
        result = cursor.fetchone()
        return result[0] if result else None


def create_botanist(conn, name: str, email: str, phone: str) -> int:
    """Create a new botanist and return the new botanist_id."""
    with conn.cursor() as cursor:
        cursor.execute(
            "INSERT INTO botanist (name, email, phone) VALUES (%s, %s, %s)",
            (name, email, phone)
        )
        cursor.execute("SELECT SCOPE_IDENTITY()")
        return cursor.fetchone()[0]


def get_or_create_botanist(conn, name: str, email: str, phone: str) -> int:
    """Get botanist_id from database, or create if doesn't exist."""
    botanist_id = get_botanist_id(conn, email)
    if botanist_id is None:
        botanist_id = create_botanist(conn, name, email, phone)
    return botanist_id


def load_botanist(conn, row: dict) -> int:
    """Load a single botanist row into the database and return botanist_id."""
    return get_or_create_botanist(
        conn,
        row["botanist_name"],
        row["botanist_email"],
        row["botanist_phone"]
    )


def load_botanists(df: pd.DataFrame) -> dict:
    """Load all unique botanists from dataframe into database.

    Returns a dict mapping botanist_email -> botanist_id for later use.
    """
    conn = get_connection()
    email_to_id = {}

    try:
        unique_botanists = df[[
            'botanist_name', 'botanist_email', 'botanist_phone']].drop_duplicates()
        for _, row in unique_botanists.iterrows():
            botanist_id = load_botanist(conn, row)
            email_to_id[row["botanist_email"]] = botanist_id
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

    return email_to_id


if __name__ == "__main__":
    conn = get_connection()
    query = "SELECT * FROM botanist"
    print(pd.read_sql(query, conn))
    conn.close()
