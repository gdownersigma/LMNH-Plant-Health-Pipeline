"""Historical plant data dashboard using AWS Athena and S3."""

from live_data_query import get_db_connection, query_database
import sys
from pathlib import Path
from os import environ as ENV
from dotenv import load_dotenv
import pandas as pd
import streamlit as st
from pyathena import connect
import altair as alt

# Add the dashboard folder to the path
sys.path.insert(0, str(Path(__file__).parent.parent))


load_dotenv()


@st.cache_resource
def get_athena_connection():
    """Create and return an Athena connection."""
    return connect(
        s3_staging_dir=f"s3://{ENV['S3_BUCKET']}/athena-results/",
        region_name=ENV.get('AWS_REGION', 'eu-west-2'),
        aws_access_key_id=ENV.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=ENV.get('AWS_SECRET_ACCESS_KEY')
    )


def query_athena(conn, query: str) -> pd.DataFrame:
    """Execute an Athena query and return results as DataFrame."""
    return pd.read_sql(query, conn)


@st.cache_data(ttl=600)
def get_unique_plants(_conn) -> pd.DataFrame:
    """Get list of unique plants from historical data."""
    query = """
    SELECT DISTINCT plant_id, plant_name
    FROM "c21_curdie_plant_catalog"."daily_plant_summaries"
    ORDER BY plant_id
    """
    return query_athena(_conn, query)


@st.cache_data(ttl=600)
def get_plant_details(_conn, plant_id: int, start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """Get aggregated details for a specific plant."""
    date_filter = ""
    if start_date and end_date:
        date_filter = f"AND reading_date BETWEEN DATE '{start_date}' AND DATE '{end_date}'"

    query = f"""
    SELECT 
        plant_name,
        scientific_name,
        botanist_name,
        AVG(avg_temperature) as avg_temperature,
        AVG(avg_humidity) as avg_humidity,
        SUM(times_watered) as total_times_watered
    FROM "c21_curdie_plant_catalog"."daily_plant_summaries"
    WHERE plant_id = {plant_id}
    {date_filter}
    GROUP BY plant_name, scientific_name, botanist_name
    """
    return query_athena(_conn, query)


@st.cache_data(ttl=600)
def get_daily_data(_conn, plant_id: int, start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """Get daily data for a specific plant."""
    date_filter = ""
    if start_date and end_date:
        date_filter = f"AND reading_date BETWEEN DATE '{start_date}' AND DATE '{end_date}'"

    query = f"""
    SELECT 
        reading_date,
        avg_temperature,
        avg_humidity,
        percentile_25_temperature,
        percentile_75_temperature,
        percentile_25_humidity,
        percentile_75_humidity
    FROM "c21_curdie_plant_catalog"."daily_plant_summaries"
    WHERE plant_id = {plant_id}
    {date_filter}
    ORDER BY reading_date
    """
    df = query_athena(_conn, query)
    df['reading_date'] = pd.to_datetime(df['reading_date'])
    return df


@st.cache_data(ttl=600)
def get_plant_date_range(_conn, plant_id: int) -> tuple:
    """Get the min and max dates available for a plant."""
    query = f"""
    SELECT 
        MIN(reading_date) as min_date,
        MAX(reading_date) as max_date
    FROM "c21_curdie_plant_catalog"."daily_plant_summaries"
    WHERE plant_id = {plant_id}
    """
    df = query_athena(_conn, query)
    if not df.empty and df.iloc[0]['min_date'] and df.iloc[0]['max_date']:
        min_date = pd.to_datetime(df.iloc[0]['min_date']).date()
        max_date = pd.to_datetime(df.iloc[0]['max_date']).date()
        return min_date, max_date
    return None, None


@st.cache_data(ttl=600)
def get_plant_image_url(_conn, plant_id: int) -> str:
    """Get the image URL for a specific plant from RDS."""
    query = f"""
        SELECT image_url
        FROM plant
        WHERE plant_id = {plant_id}
    """
    df = query_database(_conn, query)
    if not df.empty and df.iloc[0]['image_url']:
        return df.iloc[0]['image_url']
    return None


def build_select_box(df: pd.DataFrame, name: str, columns: list[str]) -> int:
    """Builds a select box sidebar component and returns the selected option."""
    options = df[columns].drop_duplicates().values.tolist()

    selected_option = st.sidebar.selectbox(
        label=f"Select {name}",
        options=options,
        format_func=lambda x: f"{x[0]} - {x[1]}"
    )

    return selected_option[0]


def display_sidebar(df: pd.DataFrame, conn) -> tuple:
    """Display the sidebar for the dashboard."""
    st.sidebar.header("Filters")

    if not df.empty:
        selected_plant_id = build_select_box(
            df, "Plant", ["plant_id", "plant_name"])

        # Get date range for the selected plant
        min_date, max_date = get_plant_date_range(conn, selected_plant_id)

        st.sidebar.divider()
        st.sidebar.subheader("Date Range")

        if min_date and max_date:
            col1, col2 = st.sidebar.columns(2)
            with col1:
                start_date = st.date_input(
                    "Start Date",
                    value=min_date,
                    min_value=min_date,
                    max_value=max_date,
                    key="start_date"
                )
            with col2:
                end_date = st.date_input(
                    "End Date",
                    value=max_date,
                    min_value=min_date,
                    max_value=max_date,
                    key="end_date"
                )
        else:
            st.sidebar.info("No date range available for this plant.")
            start_date, end_date = None, None

        return selected_plant_id, start_date, end_date

    return None, None, None


def display_plant_details(details_df: pd.DataFrame, image_url: str = None):
    """Display plant details in metrics."""
    if details_df.empty:
        st.warning("No data available for this plant.")
        return

    row = details_df.iloc[0]

    # Display image if available - centered with border
    col_left, col_img = st.columns([2, 1])
    with col_left:
        st.title("Historical Plant Data")
        st.subheader(f"🌱 Plant: {row['plant_name']}")
        st.caption(f"*Scientific Name: {row['scientific_name']}*")
    with col_img:
        with st.container(border=True):
            if image_url:
                try:
                    st.image(image_url, use_container_width=True)
                except:
                    st.image("images/plant-default.svg",
                                use_container_width=True)
            else:
                st.image("images/plant-default.svg",
                            use_container_width=True)

    st.divider()

    col1, col2, col3, col4 = st.columns([2,1,1,1])

    with col1:
        st.metric(
            label="Botanist",
            value=row['botanist_name']
        )

    with col2:
        st.metric(
            label="Times Watered",
            value=int(row['total_times_watered'])
        )

    with col3:
        st.metric(
            label="Avg Temperature",
            value=f"{row['avg_temperature']:.1f}°C"
        )

    with col4:
        st.metric(
            label="Avg Soil Moisture",
            value=f"{row['avg_humidity']:.1f}%"
        )


def display_trend_charts(daily_df: pd.DataFrame):
    """Display line charts for temperature and moisture trends."""
    if daily_df.empty:
        st.warning("No daily data available for charts.")
        return

    st.divider()
    st.subheader("📊 Historical Trends")

    col1, col2 = st.columns(2)

    with col1:
        st.write("Daily Soil Moisture")
        st.line_chart(daily_df.set_index('reading_date')['avg_humidity'])

    with col2:
        st.write("Daily Temperature")
        st.line_chart(daily_df.set_index('reading_date')['avg_temperature'])


def display_variability_chart(daily_df: pd.DataFrame):
    """Display chart showing data stability using percentiles."""
    if daily_df.empty:
        st.warning("No daily data available for variability charts.")
        return

    st.divider()
    st.subheader("📉 Reading Stability")

    # Calculate interquartile range (shows how stable readings are)
    daily_df['temp_iqr'] = daily_df['percentile_75_temperature'] - \
        daily_df['percentile_25_temperature']
    daily_df['humidity_iqr'] = daily_df['percentile_75_humidity'] - \
        daily_df['percentile_25_humidity']

    col1, col2 = st.columns(2)

    with col1:
        st.write("Temperature Variability (IQR)")
        st.line_chart(daily_df.set_index('reading_date')['temp_iqr'])

    with col2:
        st.write("Moisture Variability (IQR)")
        st.line_chart(daily_df.set_index('reading_date')['humidity_iqr'])


if __name__ == "__main__":

    st.set_page_config(page_title="Historical Plant Data", layout="wide")

    try:
        athena_conn = get_athena_connection()
        rds_conn = get_db_connection(ENV)
    except Exception as e:
        st.error(f"❌ Error connecting to database: {str(e)}")
        st.stop()

    # Get unique plants for sidebar
    plants_df = get_unique_plants(athena_conn)

    # Display sidebar and get selected plant and date range
    selected_plant_id, start_date, end_date = display_sidebar(
        plants_df, athena_conn)

    # Convert dates to string format for SQL queries
    start_date_str = start_date.strftime(
        '%Y-%m-%d') if start_date else None
    end_date_str = end_date.strftime('%Y-%m-%d') if end_date else None

    if selected_plant_id:
        # Get plant image URL from RDS
        image_url = get_plant_image_url(rds_conn, selected_plant_id)

        # Get and display plant details
        plant_details = get_plant_details(
            athena_conn, selected_plant_id, start_date_str, end_date_str)
        display_plant_details(plant_details, image_url)

        # Get and display daily data box plots
        daily_data = get_daily_data(
            athena_conn, selected_plant_id, start_date_str, end_date_str)
        display_trend_charts(daily_data)
        display_variability_chart(daily_data)
    else:
        st.info("Please select a plant from the sidebar.")

    rds_conn.close()
