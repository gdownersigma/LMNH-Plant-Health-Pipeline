"""Script to transform origin data."""
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from extract.extract import fetch_all_plants, to_dataframe


def get_raw_origin(df: pd.DataFrame) -> pd.DataFrame:
    """Extract unique origin details from the plant data."""
    origin_data = df[['origin_city', 'origin_country',
                      'origin_latitude', 'origin_longitude']]

    origin_data = origin_data.reset_index(drop=True)
    return origin_data


def validate_latitude(latitude) -> bool:
    """Validate latitude values."""
    if pd.isna(latitude):
        print(f"Validation failed: latitude is NaN")
        return False
    max_lat = 90.0
    min_lat = -90.0

    if not isinstance(latitude, (float, int)):
        print(
            f"Validation failed: latitude {latitude} is not a number (type: {type(latitude)})")
        return False

    if not (min_lat <= latitude <= max_lat):
        print(f"Validation failed: latitude {latitude} out of range [{min_lat}, {max_lat}]")
        return False
    
    
    return True


def validate_longitude(longitude) -> bool:
    """Validate longitude values."""
    if pd.isna(longitude):
        print(f"Validation failed: longitude is NaN")
        return False
    max_long = 180.0
    min_long = -180.0

    if not isinstance(longitude, (float, int)):
        print(
            f"Validation failed: longitude {longitude} is not a number (type: {type(longitude)})")
        return False

    if not (min_long <= longitude <= max_long):
        print(f"Validation failed: longitude {longitude} out of range [{min_long}, {max_long}]")
        return False
    
    return True


def validate_city_country(df: pd.DataFrame) -> bool:
    """Validate city and country data for the origin data."""

    if pd.isna(df):
        print(f"Validation failed: city/country is NaN")
        return False
    if not isinstance(df, str):
        print(f"Validation failed: city/country {df} is not a string (type: {type(df)})")
        return False
    if df.strip() == "":
        print(f"Validation failed: city/country is empty or whitespace only")
        return False
    return True


def validate_origin_data(origin_data: pd.DataFrame) -> bool:
    """Validate origin location data columns."""
    if not origin_data['origin_latitude'].apply(validate_latitude).all():
        print(f"Validation failed: lat/long contains invalid latitude values")
        return False
    
    if not origin_data['origin_longitude'].apply(validate_longitude).all():
        print(f"Validation failed: lat/long contains invalid longitude values")
        return False
    
    for col in ['origin_city', 'origin_country']:
        if not origin_data[col].apply(validate_city_country).all():
            print(f"Validation failed: column '{col}' contains invalid city/country values")
            return False
    return True


def clean_city_country(df: pd.DataFrame) -> pd.DataFrame:
    """Clean city and country data for the origin data."""

    df['origin_city'] = df['origin_city'].apply(lambda x: x.strip().title() if isinstance(x, str) else x)
    df['origin_country'] = df['origin_country'].apply(lambda x: x.strip().title() if isinstance(x, str) else x)
    return df


def clean_lat_long(df: pd.DataFrame) -> pd.DataFrame:
    """Clean latitudes and longitudes for the origin data."""

    df['origin_latitude'] = df['origin_latitude'].astype(float)
    df['origin_longitude'] = df['origin_longitude'].astype(float)
    return df


def transform_origin_data(origin_data: pd.DataFrame) -> pd.DataFrame:
    """Transform and clean origin location data."""
    origin_data = clean_city_country(origin_data)
    origin_data = clean_lat_long(origin_data)
    if validate_origin_data(origin_data):
        print("Origin data validation passed")
        return origin_data
    else:
        print("ERROR: Origin data validation failed")
        raise ValueError("Origin data validation failed.")


if __name__ == "__main__":
    pass