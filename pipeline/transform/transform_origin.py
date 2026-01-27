"""Script to transform origin data."""
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from extract.extract import fetch_all_plants, to_dataframe


def get_botanists(df: pd.DataFrame) -> pd.DataFrame:
    """Extract unique botanist details from the plant data."""
    origin_data = df[['origin_city', 'origin_country',
                      'origin_latitude', 'origin_longitude']].dropna().drop_duplicates()

    origin_data = origin_data.reset_index(drop=True)
    return origin_data


