"""File to query the live database for the dashboard."""

# pylint: disable=no-name-in-module
# pylint: disable=redefined-outer-name

from os import environ as ENV, _Environ
from dotenv import load_dotenv
from pymssql import connect, Connection
import pandas as pd
import streamlit as st


@st.cache_resource
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

    with open("dashboard/queries/plant_details.sql", "r") as file:
        query = file.read()

    return query_database(_conn, query)


@st.cache_data(ttl=600)
def get_plant_readings(_conn: Connection) -> pd.DataFrame:
    """Returns plant moisture as a DataFrame."""

    with open("dashboard/queries/plant_readings.sql", "r") as file:
        query = file.read()

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
    pass
