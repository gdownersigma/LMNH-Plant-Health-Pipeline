"""File to query the live database for the dashboard."""

from os import environ as ENV, _Environ
from dotenv import load_dotenv
from pymssql import connect, Connection
import pandas as pd
import streamlit as st


@st.cache_resource(ttl=3600)
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


@st.cache_data(ttl=60)
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


@st.cache_data(ttl=60)
def get_recent_live_data(_conn: Connection) -> pd.DataFrame:
    """Returns all data for the last readings on each plant as a DataFrame."""

    query = """
        SELECT
            p.name AS plant_name,
            p.scientific_name,
            p.image_license_url,
            p.image_url,
            p.thumbnail,
            pr.*,
            b.*,
            o.*,
            c.city_name,
            cn.*
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
        ORDER BY p.plant_id;
    """

    df = query_database(_conn, query)

    df = df.rename(columns={
        'name': 'botanist_name'
    })

    return df


# @st.cache_data(ttl=60)
# def get_filter_data(_conn: Connection) -> pd.DataFrame:
#     """Returns all live data from Database as a DataFrame."""

#     query = """
#         SELECT
#             pr.*,
#             p.name AS plant_name,
#             b.name AS botanist_name,
#             cn.country_name
#         FROM plant AS p
#         JOIN plant_reading AS pr
#             ON p.plant_id = pr.plant_id
#         JOIN botanist AS b
#             ON p.botanist_id = b.botanist_id
#         JOIN origin AS o
#             ON p.origin_id = o.origin_id
#         JOIN city AS c
#             ON o.city_id = c.city_id
#         JOIN country AS cn
#             ON c.country_id = cn.country_id
#         WHERE recording_taken > DATEADD(hour, -24, GETDATE())
#         ORDER BY p.plant_id;
#     """

#     return query_database(_conn, query)


"""
How many times has a plant been watered
Page for long term
Main page for live data
soil moisture and temperature as scatter graphs

"""

if __name__ == "__main__":

    load_dotenv()

    conn = get_db_connection(ENV)

    df = get_recent_live_data(conn)

    print(df.info())

    conn.close()
