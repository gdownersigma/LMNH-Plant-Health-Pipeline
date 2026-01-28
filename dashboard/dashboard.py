"""Dashboard file to display the plant health data."""

import pandas as pd
import streamlit as st

st.set_page_config(layout="wide", page_title="LMNH Plant Health Dashboard")


def display_sidebar(df: pd.DataFrame) -> pd.DataFrame:
    """Display the sidebar for the dashboard."""

    st.sidebar.header("Filters")

    return df  # Filtered DataFrame


def display_key_metrics():
    """Display key metrics at the top of the dashboard."""

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Total Plants",
                  value=1,
                  help="Total number of plants being monitored.")
    with col2:
        st.metric(label="Total Countries",
                  value=1,
                  help="Total number of countries of origin for the plants.")
    with col3:
        st.metric(label="Total Botanists",
                  value=1,
                  help="Total number of botanists monitoring the plants.")


def display_live_data():
    """Display live plant data chart."""
    st.subheader("Live Plant Data", text_alignment="center")


def display_all_data():
    """Display all plant data chart."""
    st.subheader("All Plant Data", text_alignment="center")


if __name__ == "__main__":
    # Get data

    st.title("LMNH Plant Health Dashboard", text_alignment="center")

    # Filter data using sidebar
    data_df = pd.DataFrame()  # Placeholder for actual data loading
    filtered_df = display_sidebar(data_df)

    display_key_metrics()

    st.header("Plant Health Overview", text_alignment="center")

    col1, col2 = st.columns(2)
    with col1:
        display_live_data()
    with col2:
        display_all_data()
