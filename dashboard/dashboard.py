"""Dashboard file to display the plant health data."""

from os import environ as ENV
from dotenv import load_dotenv
import pandas as pd
import streamlit as st

from live_data_query import (get_db_connection,
                             get_filter_data,
                             get_plant_readings,
                             get_unique_plants,
                             get_unique_countries,
                             get_unique_botanists)

from chart import (plant_scatter_chart)

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
    with col2:
        col2_1, col2_2, col2_3 = st.columns(3)

        with col2_1:
            st.metric(label="Total Plants",
                      value=plants,
                      help="Total number of plants being monitored.")
        with col2_2:
            st.metric(label="Total Countries",
                      value=countries,
                      help="Total number of countries of origin for the plants.")
        with col2_3:
            st.metric(label="Total Botanists",
                      value=botanists,
                      help="Total number of botanists monitoring the plants.")


def display_live_data(df: pd.DataFrame):
    """Display live plant data chart."""
    st.subheader(df['plant_name'].iloc[0], text_alignment="center")
    try:
        st.image(df['image_url'].iloc[0], use_container_width=True)
    except:
        st.image("images/plant-default.svg",
                 use_container_width=True)

    col1, col2 = st.columns([3, 1])
    with col1:
        chart = plant_scatter_chart(df,
                                    'recording_taken',
                                    'Time',
                                    'soil_moisture',
                                    'Soil Moisture')
        st.altair_chart(chart)

    with col2:
        col2_1, col2_2, col2_3 = st.columns([1, 2, 1])

        with col2_2:
            moisture = df.copy()
            moisture = moisture.sort_values(
                by='recording_taken', ascending=False)
            current_moisture = moisture['soil_moisture'].iloc[0]
            st.metric(label="Current Soil Moisture",
                      value=f"{current_moisture} %",
                      help="Current soil moisture level of the selected plant.")

            watered = df.copy()
            watered = watered[watered["last_watered"].dt.date ==
                              pd.Timestamp.now().date()]
            unique_watered_dates = watered['last_watered'].unique()
            last_watered = len(unique_watered_dates)
            st.metric(label="Times Watered Today",
                      value=f"{last_watered}",
                      help="Number of times the selected plant was watered today.")

    col3, col4 = st.columns([3, 1])
    with col3:
        chart = plant_scatter_chart(df,
                                    'recording_taken',
                                    'Time',
                                    'temperature',
                                    'Temperature')
        st.altair_chart(chart)

    with col4:
        col4_1, col4_2, col4_3 = st.columns([1, 2, 1])

        with col4_2:
            temps = df.copy()
            temps = temps.sort_values(by='recording_taken', ascending=False)
            current_temp = temps['temperature'].iloc[0]
            st.metric(label="Current Temperature",
                      value=f"{current_temp:.1f} °C",
                      help="Current temperature of the selected plant.")


if __name__ == "__main__":

    load_dotenv()

    conn = get_db_connection(ENV)

    filter_data_df = get_filter_data(conn)

    filter_plant_id = display_sidebar(filter_data_df)

    plant_readings_df = get_plant_readings(conn)
    filtered_plant_readings_df = plant_readings_df[
        plant_readings_df['plant_id'] == filter_plant_id]

    unique_plants = get_unique_plants(conn)
    unique_countries = get_unique_countries(conn)
    unique_botanists = get_unique_botanists(conn)

    st.title("LMNH Plant Health Dashboard", text_alignment="center")

    display_key_metrics(int(unique_plants['unique_plants'].iloc[0]),
                        int(unique_countries['unique_countries'].iloc[0]),
                        int(unique_botanists['unique_botanists'].iloc[0]))

    st.header("Plant Health Overview", text_alignment="center")

    display_live_data(filtered_plant_readings_df)

    conn.close()
