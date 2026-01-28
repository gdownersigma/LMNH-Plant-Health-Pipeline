"""Transform data for plant readings table and validate data."""

import pandas as pd


def get_plant_readings_data(all_data: pd.DataFrame) -> pd.DataFrame:
    """Extract plant readings data from the full plant data DataFrame."""

    if all_data.empty:
        raise ValueError("Input DataFrame is empty.")

    readings_columns = [
        "plant_id",
        "soil_moisture",
        "temperature",
        "recording_taken",
        "last_watered",
    ]

    if not all(col in all_data.columns for col in readings_columns):
        missing_cols = [
            col for col in readings_columns if col not in all_data.columns]
        raise KeyError(f"Missing columns in input DataFrame: {missing_cols}")

    readings_data = all_data[readings_columns].copy().dropna()
    return readings_data


def change_to_datetime(readings: pd.DataFrame, column_name: str) -> pd.DataFrame:
    """Changes columns to datetime for the plant readings data."""

    readings[column_name] = pd.to_datetime(
        readings[column_name], errors='coerce')

    return readings


def round_readings(readings: pd.DataFrame, column_name: str) -> pd.DataFrame:
    """Round soil_moisture and temperature to 3 decimal places."""

    readings[column_name] = readings[column_name].round(3)

    return readings


def round_seconds(readings: pd.DataFrame, column_name: str) -> pd.DataFrame:
    """Returns datetime column rounded to the nearest second."""

    readings[column_name] = readings[column_name].dt.round('s')

    return readings


def transform_plant_readings(all_data: pd.DataFrame) -> pd.DataFrame:
    """Transform the plant readings data."""

    readings_data = get_plant_readings_data(all_data)
    readings_data = change_to_datetime(readings_data, 'recording_taken')
    readings_data = change_to_datetime(readings_data, 'last_watered')
    readings_data = round_readings(readings_data, 'soil_moisture')
    readings_data = round_seconds(readings_data, 'recording_taken')

    return readings_data


if __name__ == "__main__":
    df = pd.read_csv("plant_data.csv")

    readings_df = get_plant_readings_data(df)
    readings_df = change_to_datetime(readings_df, 'recording_taken')
    readings_df = change_to_datetime(readings_df, 'last_watered')
    readings_df = round_readings(readings_df, 'soil_moisture')
    readings_df = round_seconds(readings_df, 'recording_taken')

    readings_df.to_csv("plant_readings.csv", index=False)
