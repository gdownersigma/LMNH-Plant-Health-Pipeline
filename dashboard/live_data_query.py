"""File to query the live database for the dashboard."""

from os import environ as ENV, _Environ
from dotenv import load_dotenv
from pymssql import connect, Connection
import pandas as pd
import streamlit as st


# @st.cache_resource
def get_db_connection(_config: _Environ) -> Connection:
    """Create and return a database connection"""
    return connect(
        server=_config['DB_HOST'],
        port=int(_config['DB_PORT']),
        user=_config['DB_USER'],
        password=_config['DB_PASSWORD'],
        database=_config['DB_NAME']
    )


def query_database(conn: Connection, query: str, parameters: dict = None) -> pd.DataFrame:
    """Returns a query result."""

    with conn.cursor() as cur:
        if parameters:
            cur.execute(query, parameters)
        else:
            cur.execute(query)

        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]

    return pd.DataFrame(rows, columns=columns)


@st.cache_data(ttl=600)
def get_filter_data(_conn: Connection) -> pd.DataFrame:
    """Returns all live data from Database as a DataFrame."""

    query = """
        SELECT
            p.plant_id,
            p.name AS plant_name,
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
        ORDER BY p.plant_id;
    """

    return query_database(_conn, query)


@st.cache_data(ttl=600)
def get_plant_readings(_conn: Connection) -> pd.DataFrame:
    """Returns plant moisture as a DataFrame."""

    query = """
        SELECT
            pr.plant_id,
            p.name AS plant_name,
            pr.soil_moisture,
            pr.temperature,
            pr.last_watered,
            pr.recording_taken
        FROM plant_reading AS pr
        JOIN plant AS p 
            ON pr.plant_id = p.plant_id
        WHERE recording_taken > DATEADD(hour, -24, GETDATE())
    """

    return query_database(_conn, query)


@st.cache_data(ttl=600)
def get_unique_plants(_conn: Connection) -> pd.DataFrame:
    """Returns unique plants."""

    query = """
        SELECT
            count(*) AS unique_plants
        FROM plant;
    """

    return query_database(_conn, query)


@st.cache_data(ttl=600)
def get_unique_countries(_conn: Connection) -> pd.DataFrame:
    """Returns unique countries."""

    query = """
        SELECT
            count(*) AS unique_countries
        FROM country;
    """

    return query_database(_conn, query)


@st.cache_data(ttl=600)
def get_unique_botanists(_conn: Connection) -> pd.DataFrame:
    """Returns unique botanists."""

    query = """
        SELECT
            count(*) AS unique_botanists
        FROM botanist;
    """

    return query_database(_conn, query)


if __name__ == "__main__":

    load_dotenv()

    conn = get_db_connection(ENV)

    df = get_plant_readings(conn)

    print(df.info())

    conn.close()
