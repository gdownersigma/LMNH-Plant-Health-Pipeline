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

    not_null_columns = [
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
        subset=not_null_columns, how='all')

    return plant_data


def clean_names(name: str) -> str:
    """Clean and standardise names."""
    if pd.isna(name) or name == '':
        return None

    name = re.sub(r'[()`\'\u2018\u2019]', '', name)
    name = re.sub(r'\s+', ' ', name)

    name = name.title().strip()

    return name


def filter_url(url: str) -> str:
    """Ensure URL starts with http or https."""
    if pd.isna(url) or url == '':
        return None

    if 'upgrade_access' in url:
        return None

    return url


def match_url_data(df: pd.DataFrame, url_column: str, has_data: pd.Series) -> pd.DataFrame:
    """Ensure that image URLs match their corresponding license URLs."""
    df.loc[~has_data, url_column] = None
    return df


def transform_plant_data(all_data: pd.DataFrame) -> pd.DataFrame:
    """Transform the plant data."""

    plant_data = get_plant_data(all_data)
    plant_data['name'] = plant_data['name'].apply(clean_names)
    plant_data['scientific_name'] = plant_data['scientific_name'].apply(
        clean_names)

    # Ensure coordinates match the format stored in origin table
    plant_data['origin_latitude'] = plant_data['origin_latitude'].astype(float)
    plant_data['origin_longitude'] = plant_data['origin_longitude'].astype(
        float)

    plant_data['image_original_url'] = plant_data['image_original_url'].apply(
        filter_url)

    has_original_url = plant_data['image_original_url'].notna()
    plant_data = match_url_data(
        plant_data, 'image_license_url', has_original_url)
    plant_data = match_url_data(
        plant_data, 'image_thumbnail', has_original_url)

    return plant_data


if __name__ == "__main__":
    df = pd.read_csv("out.csv")

    plant_df = transform_plant_data(df)

    plant_df.to_csv("plant_data.csv", index=False)
