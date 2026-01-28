"""Transform data for the plant table and validate data."""

import re

import pandas as pd


def get_plant_data(all_data: pd.DataFrame) -> pd.DataFrame:
    """Extract plant data from the full plant data DataFrame."""

    if all_data.empty:
        raise ValueError("Input DataFrame is empty.")

    plant_columns = [
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

    important_columns = [
        "name",
        "botanist_email",
        "origin_latitude",
        "origin_longitude"
    ]

    if not all(col in all_data.columns for col in plant_columns):
        missing_cols = [
            col for col in plant_columns if col not in all_data.columns]
        raise KeyError(f"Missing columns in input DataFrame: {missing_cols}")

    plant_data = all_data[plant_columns].copy().dropna(
        subset=important_columns, how='all')

    return plant_data


def clean_names(name: str) -> str:
    """Clean and standardise names."""
    if pd.isna(name) or name == '':
        return None

    name = re.sub(r'[()`\'\u2018\u2019]', '', name)
    name = re.sub(r'\s+', ' ', name)

    name = name.title().strip()

    return name


def transform_plant_data(all_data: pd.DataFrame) -> pd.DataFrame:
    """Transform the plant data."""

    plant_data = get_plant_data(all_data)
    plant_data['name'] = plant_data['name'].apply(clean_names)
    plant_data['scientific_name'] = plant_data['scientific_name'].apply(
        clean_names)

    return plant_data


if __name__ == "__main__":
    df = pd.read_csv("out.csv")

    plant_df = transform_plant_data(df)

    plant_df.to_csv("plant_data.csv", index=False)
