"""Dashboard file to display the plant health data."""

from os import environ as ENV
import re
from dotenv import load_dotenv
import pandas as pd
import streamlit as st

from data_query import get_db_connection, get_filter_data, get_all_live_data

st.set_page_config(layout="wide", page_title="LMNH Plant Health Dashboard")


def build_multiselect(df: pd.DataFrame, name: str, columns: list[str], default: bool) -> list:
    """Builds a multiselect and checkmark sidebar component and returns the selected options."""
    options = df[columns].drop_duplicates().values.tolist()

    select_all = st.sidebar.checkbox(
        f"Select All {name}s", value=default)

    selected_options = st.sidebar.multiselect(
        label=f"Select {name}s",
        options=options,
        default=options if select_all else [],
        format_func=lambda x: f"{x[0]}" if name != "Plant" else f"{x[0]} - {x[1]}"
    )

    return [option[0] for option in selected_options]


def display_sidebar(df: pd.DataFrame) -> pd.Series:
    """Display the sidebar for the dashboard."""

    st.sidebar.header("Filters")

    if not df.empty:
        selected_plant_ids = build_multiselect(
            df, "Plant", ["plant_id", "name"], default=True)

        selected_botanist_names = build_multiselect(
            df, "Botanist", ["botanist_name"], default=True)

        selected_country_names = build_multiselect(
            df, "Country", ["country_name"], default=True)

        return df['plant_id'].isin(selected_plant_ids) & \
            df['botanist_name'].isin(selected_botanist_names) & \
            df['country_name'].isin(selected_country_names)

    return df['plant_id'].isin([])


def display_key_metrics(plants: int, countries: int, botanists: int):
    """Display key metrics at the top of the dashboard."""

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Total Plants",
                  value=plants,
                  help="Total number of plants being monitored.")
    with col2:
        st.metric(label="Total Countries",
                  value=countries,
                  help="Total number of countries of origin for the plants.")
    with col3:
        st.metric(label="Total Botanists",
                  value=botanists,
                  help="Total number of botanists monitoring the plants.")


def display_live_data(df: pd.DataFrame):
    """Display live plant data chart."""
    st.subheader("Live Plant Data", text_alignment="center")


def display_all_data():
    """Display all plant data chart."""
    st.subheader("All Plant Data", text_alignment="center")


def join_all_data():
    """Returns joined data from plant, botanist, and country dataframes."""
    pass


if __name__ == "__main__":

    load_dotenv()

    conn = get_db_connection(ENV)

    filter_data_df = get_filter_data(conn)
    all_live_data_df = get_all_live_data(conn)

    conn.close()

    filter_condition = display_sidebar(filter_data_df)
    filtered_live_data_df = all_live_data_df[filter_condition]

    st.title("LMNH Plant Health Dashboard", text_alignment="center")

    display_key_metrics(int(filtered_live_data_df['plant_id'].nunique()),
                        int(filtered_live_data_df['country_id'].nunique()),
                        int(filtered_live_data_df['botanist_id'].nunique()))

    st.header("Plant Health Overview", text_alignment="center")

    col1, col2 = st.columns(2)
    with col1:
        display_live_data(filtered_live_data_df)
    with col2:
        display_all_data()
