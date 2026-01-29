"""File to query the long term S3 for the dashboard."""

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


if __name__ == "__main__":

    load_dotenv()

    conn = get_db_connection(ENV)

    conn.close()
