"""File to query the database and S3 for the dashboard."""

from os import environ as ENV, _Environ
from dotenv import load_dotenv
from pymssql import connect, Connection
import pandas as pd
import streamlit as st


def get_db_connection(config: _Environ) -> Connection:
    """Create and return a database connection"""
    return connect(
        server=config['DB_HOST'],
        port=int(config['DB_PORT']),
        user=config['DB_USER'],
        password=config['DB_PASSWORD'],
        database=config['DB_NAME']
    )


def get_all_live_data(conn: Connection) -> pd.DataFrame:
    """Returns all live data from Database as a DataFrame."""

    with conn.cursor() as cur:
        cur.execute(
            f"""SELECT
                    p.*,
                    pr.plant_reading_id,
                    pr.soil_moisture,
                    pr.temperature,
                    pr.recording_taken,
                    pr.last_watered,
                    b.email,
                    b.name AS botanist_name,
                    b.phone,
                    o.lat,
                    o.long,
                    c.city_id,
                    c.city_name,
                    cn.country_id,
                    cn.country_name
                FROM plant AS p 
                JOIN plant_reading AS pr
                    ON p.plant_id = pr.plant_id
                JOIN botanist AS b
                    ON p.botanist_id = b.botanist_id
                JOIN origin AS o
                    ON p.origin_id = o.origin_id
                JOIN city AS c
                    ON o.city_id = c.city_id
                JOIN country AS cn
                    ON c.country_id = cn.country_id
                WHERE pr.plant_reading_id IN (
                    SELECT MAX(plant_reading_id)
                    FROM plant_reading
                    GROUP BY plant_id)
                ORDER BY p.plant_id;""")
        columns = [desc[0] for desc in cur.description]
        data = cur.fetchall()

    df = pd.DataFrame(data, columns=columns)
    return df


def get_filter_data(conn: Connection) -> pd.DataFrame:
    """Returns all live data from Database as a DataFrame."""

    with conn.cursor() as cur:
        cur.execute(
            f"""SELECT
                    p.plant_id,
                    p.name,
                    b.botanist_id,
                    b.name AS botanist_name,
                    cn.country_id,
                    cn.country_name
                FROM plant AS p 
                JOIN botanist AS b
                    ON p.botanist_id = b.botanist_id
                JOIN origin AS o
                    ON p.origin_id = o.origin_id
                JOIN city AS c
                    ON o.city_id = c.city_id
                JOIN country AS cn
                    ON c.country_id = cn.country_id
                ORDER BY p.plant_id;""")
        columns = [desc[0] for desc in cur.description]
        data = cur.fetchall()

    df = pd.DataFrame(data, columns=columns)
    return df


if __name__ == "__main__":

    load_dotenv()

    conn = get_db_connection(ENV)

    df = get_all_live_data(conn)

    print(df.head())

    conn.close()
