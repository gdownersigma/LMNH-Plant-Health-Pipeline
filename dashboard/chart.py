"""File to create the charts for the dashboard."""

import pandas as pd
import streamlit as st
import altair as alt


@st.cache_data(ttl=60)
def plant_bar_chart(df: pd.DataFrame, y_field: str, y_title: str) -> alt.Chart:
    """Create a bar of live plant data."""

    print("Test3")
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('plant_id:N',
                title='Plant',
                axis=alt.Axis(labels=False)).sort('-y'),
        y=alt.Y(f'{y_field}:Q', title=y_title),
        color=alt.Color('name:N')
    ).properties(
        title=f'Plant vs {y_title}',
        width=600,
        height=400
    )

    return chart
