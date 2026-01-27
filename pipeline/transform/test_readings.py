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


def test_fix_data_types(valid_readings_data: pd.DataFrame):
    """Test changing of data types for plant readings data."""
    original_dtype = valid_readings_data["recording_taken"].dtype
    fixed_data = fix_data_types(valid_readings_data, 'recording_taken')
    new_dtype = fixed_data["recording_taken"].dtype
    print(new_dtype)

    assert not pd.api.types.is_datetime64_any_dtype(original_dtype)
    assert pd.api.types.is_datetime64_any_dtype(new_dtype)
