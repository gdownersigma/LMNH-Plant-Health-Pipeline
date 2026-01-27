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


if __name__ == "__main__":
    pass