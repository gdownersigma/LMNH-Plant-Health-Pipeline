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

    readings_data = all_data[readings_columns].copy()
    return readings_data


def validate_data_types(readings: pd.DataFrame) -> bool:
    """Validate data types for the plant readings data columns."""
    pass
