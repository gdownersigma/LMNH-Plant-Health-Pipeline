"""Dashboard file to display the plant health data."""

from os import environ as ENV
from dotenv import load_dotenv
import pandas as pd
import streamlit as st

from live_data_query import (get_db_connection,
                             get_filter_data,
                             get_plant_moisture_over_time,
                             get_unique_plants,
                             get_unique_countries,
                             get_unique_botanists)

from chart import (plant_line_chart)

st.set_page_config(layout="wide", page_title="LMNH Plant Health Dashboard")


def build_multi_select(df: pd.DataFrame, name: str, columns: list[str], default: bool) -> list:
    """Builds a multiselect and checkbox sidebar component and returns the selected options."""
    options = df[columns].drop_duplicates().values.tolist()

    select_all = st.sidebar.checkbox(
        f"Select All {name}", value=default)

    selected_options = st.sidebar.multiselect(
        label=f"Select {name}",
        options=options,
        default=options if select_all else [],
        format_func=lambda x: f"{x[0]}" if name != "Plants" else f"{x[0]} - {x[1]}"
    )

    return [option[0] for option in selected_options]


def build_select_box(df: pd.DataFrame, name: str, columns: list[str]) -> int:
    """Builds a select box sidebar component and returns the selected option."""
    options = df[columns].drop_duplicates().values.tolist()

    selected_option = st.sidebar.selectbox(
        label=f"Select {name}",
        options=options,
        format_func=lambda x: f"{x[0]}" if name != "Plant" else f"{x[0]} - {x[1]}"
    )

    print(selected_option)

    return selected_option[0]


def display_sidebar(df: pd.DataFrame) -> int:
    """Display the sidebar for the dashboard."""

    st.sidebar.header("Filters")

    if not df.empty:
        selected_plant_id = build_select_box(
            df, "Plant", ["plant_id", "plant_name"])

        return selected_plant_id

    return 1


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

    col1, col2 = st.columns([3, 1])
    with col1:
        print(df.info())
        df['hour'] = df['recording_taken'].dt.hour
        df['minute'] = df['recording_taken'].dt.minute
        df['time'] = df['hour'].astype(str).str.zfill(
            2) + ':' + df['minute'].astype(str).str.zfill(2)
        chart = plant_line_chart(df,
                                 'time',
                                 'Time (HH:MM)',
                                 'soil_moisture',
                                 'Soil Moisture')
        st.altair_chart(chart)

        # chart = plant_line_chart(df, 'temperature', 'Temperature')
        # st.altair_chart(chart)

    with col2:
        pass


if __name__ == "__main__":

    load_dotenv()

    conn = get_db_connection(ENV)

    filter_data_df = get_filter_data(conn)

    filter_plant_id = display_sidebar(filter_data_df)

    plant_moisture_over_time_df = get_plant_moisture_over_time(
        conn, filter_plant_id)

    unique_plants = get_unique_plants(conn)
    unique_countries = get_unique_countries(conn)
    unique_botanists = get_unique_botanists(conn)

    st.title("LMNH Plant Health Dashboard", text_alignment="center")

    display_key_metrics(int(unique_plants['unique_plants'].iloc[0]),
                        int(unique_countries['unique_countries'].iloc[0]),
                        int(unique_botanists['unique_botanists'].iloc[0]))

    st.header("Plant Health Overview", text_alignment="center")

    display_live_data(plant_moisture_over_time_df)

    conn.close()
