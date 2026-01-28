"""Test transform functions for plant data."""

import pandas as pd
import pytest
from transform_plants import get_plant_data, clean_names, transform_plant_data


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


@pytest.mark.parametrize("input, output", [
    ["venus flytrap", "Venus Flytrap"],
    ["Canna ‘Striata’", "Canna Striata"],
    ["Heliconia schiedeana 'Fire and Ice'", "Heliconia Schiedeana Fire And Ice"],
    ["Spathiphyllum (group)", "Spathiphyllum Group"],
    ["", None],
    [None, None],
    ["    Chlorophytum     comosum 'Vittatum'", "Chlorophytum Comosum Vittatum"]
])
def test_clean_names(input, output):
    assert clean_names(input) == output


def test_transform_plant_data(sample_plant_data_full, sample_transformed_plant_table_data):
    """Test full transformation of plant data."""
    input_df = pd.json_normalize(sample_plant_data_full)
    output_df = pd.json_normalize(sample_transformed_plant_table_data)

    transformed_data = transform_plant_data(input_df)

    assert list(transformed_data.columns) == list(output_df.columns)
    assert transformed_data["name"].iloc[0] == output_df["name"].iloc[0]
    assert transformed_data["scientific_name"].iloc[0] == output_df["scientific_name"].iloc[0]
