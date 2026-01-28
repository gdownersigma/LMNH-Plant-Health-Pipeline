"""Tests for readings transformation functions."""

import pandas as pd
import pytest
from transform_readings import (
    get_plant_readings_data, fix_data_types, round_readings, round_seconds)


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
def test_round_readings(column_name, valid_readings_data: pd.DataFrame):
    """Test rounding for plant readings data."""
    original_value = valid_readings_data[column_name].iloc[0]
    readings_data = round_readings(valid_readings_data, column_name)
    rounded_value = readings_data[column_name].iloc[0]

    assert isinstance(rounded_value, float)
    assert round(original_value, 3) == rounded_value
    assert len(str(rounded_value).rsplit('.', maxsplit=1)[-1]) <= 3


@pytest.mark.parametrize("column_name", [
    'recording_taken',
])
def test_round_seconds(column_name, valid_readings_data: pd.DataFrame):
    """Test removal of milliseconds for plant readings data."""
    readings_data = fix_data_types(valid_readings_data, column_name)

    original_value = readings_data[column_name].iloc[0]
    readings_data = round_seconds(readings_data, column_name)
    new_value = readings_data[column_name].iloc[0]

    assert isinstance(original_value, pd.Timestamp)
    assert isinstance(new_value, pd.Timestamp)
    assert original_value.microsecond != 0
    assert new_value.microsecond == 0
