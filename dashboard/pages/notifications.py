"""Generate page which displays notifications on which plants need attention."""

from os import environ as ENV
from dotenv import load_dotenv
from datetime import datetime
import pandas as pd
import streamlit as st
from dashboard.live_data_query import get_db_connection, query_database


def get_watering_data(conn) -> pd.DataFrame:
    """Query plants that need watering."""
    cutoff = datetime.now() - pd.to_timedelta(1, unit='d')
    query = """
    SELECT
        p.plant_id,
        p.name AS plant_name,
        p.last_watered,
    FROM plant AS p;
    """
    return query_database(conn, query, (cutoff,))


def gen_needs_watering_section(conn):
    """Generate section for plants that need watering."""
    df = get_watering_data(conn)

    # Calculate days since watered
    df['Days Since Watered'] = (
        datetime.now() - df['last_watered']).dt.total_seconds() / (24 * 3600)
    df['Days Since Watered'] = df['Days Since Watered'].round(1)

    def style_rows(row):
        days = row['Days Since Watered']
        if days > 3:
            return ['background-color: #ffcccc'] * len(row)  # Light red
        elif days > 1:
            return ['background-color: #ffffcc'] * len(row)  # Light yellow
        else:
            return ['background-color: white'] * len(row)

    # Apply styling and display
    st.title("Plant Watering Status")
    styled_df = df.style.apply(style_rows, axis=1)
    st.dataframe(styled_df, use_container_width=True)


if __name__ == "__main__":

    load_dotenv()

    conn = get_db_connection(ENV)

    st.title("Plant Notifications")
    gen_needs_watering_section(conn)

    conn.close()
