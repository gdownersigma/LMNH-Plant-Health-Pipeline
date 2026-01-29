"""File to query the long term S3 for the dashboard."""

from os import environ as ENV, _Environ
from dotenv import load_dotenv

from pyathena import connect
from pyathena.connection import Connection
import pandas as pd
import streamlit as st


def get_athena_connection(config: _Environ) -> Connection:
    """Returns a live Athena connection using pyathena."""

    return connect(
        s3_staging_dir=config["S3_STAGING_DIR"],
        region_name=config["REGION"],
        schema_name=config["SCHEMA_NAME"],
        aws_access_key_id=config["ACCESS_KEY_ID"],
        aws_secret_access_key=config["SECRET_ACCESS_KEY"]
    )


def query_athena(conn: Connection, query: str, parameters: dict = None) -> pd.DataFrame:
    """Returns a query result."""

    with conn.cursor() as cur:
        if parameters:
            cur.execute(query, parameters)
        else:
            cur.execute(query)

        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]

    return pd.DataFrame(rows, columns=columns)


if __name__ == "__main__":

    load_dotenv()

    conn = get_athena_connection(ENV)

    df = query_athena(
        conn,
        """
            SELECT
                p.*
            FROM plant AS p
            ORDER BY p.plant_id;
        """
    )
    print(df.info())

    conn.close()
