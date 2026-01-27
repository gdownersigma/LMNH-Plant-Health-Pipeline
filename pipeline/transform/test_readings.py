"""Tests for readings transformation functions."""

import pandas as pd
import pytest
from transform_readings import (
    get_plant_readings_data, fix_data_types, round_readings, remove_milliseconds)


def test_get_plant_readings_data(sample_plant_data):
    """Test extraction of plant readings data."""
    df = pd.json_normalize(sample_plant_data)
    readings_data = get_plant_readings_data(df)

    expected_columns = [
        "plant_id",
        "soil_moisture",
        "temperature",
        "recording_taken",
        "last_watered",
    ]

    assert list(readings_data.columns) == expected_columns
    assert readings_data["plant_id"].iloc[0] == sample_plant_data["plant_id"]


def test_get_plant_readings_data_empty():
    """Test extraction with empty DataFrame."""
    empty_df = pd.DataFrame()

    with pytest.raises(ValueError, match="Input DataFrame is empty."):
        get_plant_readings_data(empty_df)


@pytest.mark.parametrize("column_name", [
    'recording_taken',
    'last_watered'
])
def test_fix_data_types(column_name, valid_readings_data: pd.DataFrame):
    """Test changing of data types for plant readings data."""
    original_dtype = valid_readings_data[column_name].dtype
    fixed_data = fix_data_types(valid_readings_data, column_name)
    new_dtype = fixed_data[column_name].dtype
    print(new_dtype)

    assert not pd.api.types.is_datetime64_any_dtype(original_dtype)
    assert pd.api.types.is_datetime64_any_dtype(new_dtype)


@pytest.mark.parametrize("column_name", [
    'soil_moisture',
    'temperature'
])
def test_round_readings_for_soil_moisture(column_name, valid_readings_data: pd.DataFrame):
    """Test rounding for plant readings data."""
    original_soil_moisture = valid_readings_data[column_name].iloc[0]
    readings_data = round_readings(valid_readings_data, column_name)
    rounded_soil_moisture = readings_data[column_name].iloc[0]

    print(original_soil_moisture)
    print(rounded_soil_moisture)

    assert isinstance(rounded_soil_moisture, float)
    assert round(original_soil_moisture, 3) == rounded_soil_moisture
    assert len(str(rounded_soil_moisture).split('.')[-1]) <= 3
