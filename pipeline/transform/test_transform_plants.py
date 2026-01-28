"""Test transform functions for plant data."""

import pandas as pd
import pytest
from transform_plants import get_plant_data


def test_get_plant_data(sample_plant_data_full):
    """Test extraction of plant data."""
    df = pd.json_normalize(sample_plant_data_full)
    plant_data = get_plant_data(df)

    expected_columns = [
        "plant_id",
        "name",
        "scientific_name",
        "botanist_email",
        "origin_latitude",
        "origin_longitude",
        "image_license_url",
        "image_original_url",
        "image_thumbnail"
    ]

    assert list(plant_data.columns) == expected_columns
    assert plant_data["plant_id"].iloc[0] == sample_plant_data_full["plant_id"]
