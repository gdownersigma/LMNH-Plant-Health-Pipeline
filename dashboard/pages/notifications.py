"""Generate page which displays notifications on which plants need attention."""

import sys
from pathlib import Path
from os import environ as ENV
from dotenv import load_dotenv
from datetime import datetime
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# Add the dashboard folder to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from live_data_query import get_db_connection, query_database


@st.cache_data(ttl=600)
def get_plant_readings(_conn) -> pd.DataFrame:
    """Returns plant moisture as a DataFrame."""

    query = """
        SELECT
            pr.plant_id,
            p.name AS plant_name,
            pr.soil_moisture,
            pr.temperature,
            pr.last_watered,
            pr.recording_taken,
            p.image_url,
            b.name AS botanist_name
        FROM plant_reading AS pr
        JOIN (
            SELECT plant_id, MAX(recording_taken) AS max_recording
            FROM plant_reading
            GROUP BY plant_id
        ) AS latest 
            ON pr.plant_id = latest.plant_id 
            AND pr.recording_taken = latest.max_recording
        JOIN plant AS p 
            ON pr.plant_id = p.plant_id
        JOIN botanist AS b
            ON p.botanist_id = b.botanist_id
    """
    return query_database(_conn, query)

def gen_needs_watering_section(df):
    """Generate section for plants that need watering."""

    # Calculate days since watered
    df['Days Since Watered'] = (
        datetime.now() - df['last_watered']).dt.total_seconds() / (24 * 3600)
    df['Days Since Watered'] = df['Days Since Watered'].round(2)
    df = df.sort_values('Days Since Watered', ascending=False)

    def style_rows(row):
        days = row['Days Since Watered']
        if days > 2:
            return ['background-color: #ffcccc'] * len(row)  # Light red
        elif days > 1:
            return ['background-color: #ffffcc'] * len(row)  # Light yellow
        else:
            return ['background-color: white'] * len(row)

    # Apply styling and display
    st.title("Plant Watering Status")
    styled_df = df[['plant_name', 'last_watered',
                    'Days Since Watered', 'botanist_name']].style.apply(style_rows, axis=1).format({
                        'last_watered': lambda t: t.strftime("%Y-%m-%d %H:%M"),
                        'Days Since Watered': "{:.2f}"
                    })
    st.dataframe(styled_df, use_container_width=True, hide_index=True)

def gen_low_soil_moisture_section(df):
    """Generate a scatter graph of plant_id vs soil_moisture. Highlight plants with soil_moisture < 30%."""

    st.title("Soil Moisture Levels")

    # Calculate outliers using IQR method
    Q1 = df['soil_moisture'].quantile(0.25)
    Q3 = df['soil_moisture'].quantile(0.75)
    IQR = Q3 - Q1

    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    if upper_bound > 100:
        upper_bound = 100


    # Identify outliers
    df['is_outlier'] = (df['soil_moisture'] < lower_bound) | (
        df['soil_moisture'] > upper_bound)

    # Create a color list based on outlier status
    colors = ['red' if outlier else 'blue' for outlier in df['is_outlier']]

    # Create the scatter plot
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(df['plant_id'], df['soil_moisture'], c=colors, s=100, alpha=0.6)

    # Add lines for outlier boundaries
    ax.axhline(y=lower_bound, color='orange', linestyle='--',
            label=f'Lower Bound ({lower_bound:.2f})')
    ax.axhline(y=upper_bound, color='orange', linestyle='--',
            label=f'Upper Bound ({upper_bound:.2f})')

    ax.set_xlabel('Plant ID')
    ax.set_ylabel('Soil Moisture (%)')
    ax.set_title('Plant Soil Moisture Levels (Outliers Highlighted)')
    ax.legend()
    ax.grid(True, alpha=0.3)

    st.pyplot(fig)

    outliers = df[df['is_outlier']]

    if len(outliers) > 0:
        st.warning("⚠️ **Outlier Plants Detected**")

        # Create grid with 4 columns
        cols = st.columns(4)

        for idx, (_, row) in enumerate(outliers.iterrows()):
            col = cols[idx % 4]

            with col:
                with st.container(border=True):
                    try:
                        st.image(row['image_url'], use_container_width=True)
                    except:
                        st.image("plant-default.svg",
                                use_container_width=True)  # Fallback image

                    # Display plant info
                    st.write(f"**{row['plant_name']}**")
                    st.write(f"ID: {row['plant_id']}")
                    st.write(f"Botanist: {row['botanist_name']}")
                    st.write(f"Moisture: {row['soil_moisture']:.2f}%")
    else:
        st.success("✓ No outliers detected")


def gen_outlier_temp_section(df):
    """Generate a scatter graph of plant_id vs temperature. Highlight plants with temperature outliers."""

    st.title("Temperature Levels")

    # Calculate outliers using IQR method
    Q1 = df['temperature'].quantile(0.25)
    Q3 = df['temperature'].quantile(0.75)
    IQR = Q3 - Q1

    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    if upper_bound > 100:
        upper_bound = 50

    # Identify outliers
    df['is_outlier'] = (df['temperature'] < lower_bound) | (
        df['temperature'] > upper_bound)

    # Create a color list based on outlier status
    colors = ['red' if outlier else 'blue' for outlier in df['is_outlier']]

    # Create the scatter plot
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(df['plant_id'], df['temperature'], c=colors, s=100, alpha=0.6)

    # Add lines for outlier boundaries
    ax.axhline(y=lower_bound, color='orange', linestyle='--',
               label=f'Lower Bound ({lower_bound:.2f})')
    ax.axhline(y=upper_bound, color='orange', linestyle='--',
               label=f'Upper Bound ({upper_bound:.2f})')

    ax.set_xlabel('Plant ID')
    ax.set_ylabel('Temperature (°C)')
    ax.set_title('Plant Temperature Levels (Outliers Highlighted)')
    ax.legend()
    ax.grid(True, alpha=0.3)

    st.pyplot(fig)

    outliers = df[df['is_outlier']]

    if len(outliers) > 0:
        st.warning("⚠️ **Outlier Plants Detected**")

        # Create grid with 4 columns
        cols = st.columns(4)

        for idx, (_, row) in enumerate(outliers.iterrows()):
            col = cols[idx % 4]

            with col:
                with st.container(border=True):
                    try:
                        st.image(row['image_url'], use_container_width=True)
                    except:
                        st.image("plant-default.svg",
                                 use_container_width=True)  # Fallback image

                    # Display plant info
                    st.write(f"**{row['plant_name']}**")
                    st.write(f"ID: {row['plant_id']}")
                    st.write(f"Botanist: {row['botanist_name']}")
                    st.write(f"Temperature: {row['temperature']:.2f}°C")
    else:
        st.success("✓ No outliers detected")


if __name__ == "__main__":

    st.set_page_config(page_title="Plant Notifications", layout="wide")

    load_dotenv()

    conn = get_db_connection(ENV)
    df = get_plant_readings(conn)

    st.title("Plant Notifications")
    gen_needs_watering_section(df)
    gen_low_soil_moisture_section(df)
    gen_outlier_temp_section(df)
    conn.close()