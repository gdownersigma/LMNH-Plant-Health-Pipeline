"""File to create the charts for the dashboard."""

import pandas as pd
import streamlit as st
import altair as alt


@st.cache_data(ttl=60)
def plant_line_chart(df: pd.DataFrame,
                     x_field: str,
                     x_title: str,
                     y_field: str,
                     y_title: str) -> alt.Chart:
    """Create a line chart of live plant data."""

    chart = alt.Chart(df).mark_point().encode(
        x=alt.X(f'{x_field}:N',
                title=x_title),
        y=alt.Y(f'{y_field}:Q',
                title=y_title),
        color=alt.Color('plant_name:N',
                        title='Plant Name')
    ).properties(
        title=f'Plant vs {y_title} over time',
        width=600,
        height=400
    )

    return chart
