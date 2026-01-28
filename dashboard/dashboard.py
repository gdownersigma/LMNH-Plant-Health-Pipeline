"""Dashboard file to display the plant health data."""

from os import environ as ENV
import re
from dotenv import load_dotenv
import pandas as pd
import streamlit as st

from data_query import get_db_connection, get_key_metrics

st.set_page_config(layout="wide", page_title="LMNH Plant Health Dashboard")


def build_multiselect(name: str, options: list, default: bool) -> list:
    """"""
    select_all = st.sidebar.checkbox(
        f"Select All {name}s", value=default)

    selected_options = st.sidebar.multiselect(
        label=f"Select {name}s",
        options=options,
        default=options if select_all else [],
        # format_func=lambda x: f"{x}" if name != "Plant" else f"{x[0]} - {x[1]}"
    )

    return selected_options


def display_sidebar(df: pd.DataFrame) -> pd.DataFrame:
    """Display the sidebar for the dashboard."""

    st.sidebar.header("Filters")

    if not df.empty:
        # Use IDs for filtering to avoid issues with duplicate names
        plant_tuples = df[['plant_id', 'plant_name']
                          ].drop_duplicates().values.tolist()
        plant_tuples = [tuple(row) for row in plant_tuples]

        # Checkbox to select or deselect all plants
        # select_all_plants = st.sidebar.checkbox(
        #     "Select All Plants", value=True)

        # # Multiselect dropdown for plants
        # selected_plants = st.sidebar.multiselect(
        #     label="Select Plants",
        #     options=plant_tuples,
        #     default=plant_tuples if select_all_plants else [],
        #     format_func=lambda x: f"{x[0]} - {x[1]}"
        # )

        selected_plants = build_multiselect(
            "Plant", plant_tuples, default=True)

        # Get unique botanist names for filtering
        botanist_names = df['botanist_name'].drop_duplicates().values.tolist()

        # Checkbox to select or deselect all botanists
        # select_all_botanists = st.sidebar.checkbox(
        #     "Select All Botanists", value=True)

        # # Multiselect dropdown for botanists
        # selected_botanist_names = st.sidebar.multiselect(
        #     label="Select Botanists",
        #     options=botanist_names,
        #     default=botanist_names if select_all_botanists else []
        # )

        selected_botanist_names = build_multiselect(
            "Botanist", botanist_names, default=True)

        # Get unique country names for filtering
        country_names = df['country_name'].drop_duplicates().values.tolist()

        # Checkbox to select or deselect all countries
        # select_all_countries = st.sidebar.checkbox(
        #     "Select All Countries", value=True)

        # # Multiselect dropdown for countries
        # selected_country_names = st.sidebar.multiselect(
        #     label="Select Countries",
        #     options=country_names,
        #     default=country_names if select_all_countries else []
        # )

        selected_country_names = build_multiselect(
            "Country", country_names, default=True)

        selected_plant_ids = [plant[0] for plant in selected_plants]

        filtered_df = df[df['plant_id'].isin(selected_plant_ids) &
                         df['botanist_name'].isin(selected_botanist_names) &
                         df['country_name'].isin(selected_country_names)].copy()
        return filtered_df

    return df


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


def display_live_data():
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

    # Get data
    conn = get_db_connection(ENV)

    all_data_df = get_key_metrics(conn)

    conn.close()

    filtered_df = display_sidebar(all_data_df)

    st.title("LMNH Plant Health Dashboard", text_alignment="center")

    display_key_metrics(int(all_data_df['plant_id'].nunique()),
                        int(all_data_df['country_id'].nunique()),
                        int(all_data_df['botanist_id'].nunique()))

    st.header("Plant Health Overview", text_alignment="center")

    col1, col2 = st.columns(2)
    with col1:
        display_live_data()
    with col2:
        display_all_data()
