"""The code to run the ETL pipeline."""

from extract.extract import fetch_all_plants, to_dataframe
from transform.transform_origin import get_raw_origin, transform_origin_data
from load.load_origin import load_origins


if __name__ == "__main__":
    # Extract
    all_plants = fetch_all_plants()
    plants_df = to_dataframe(all_plants)

    # Transform
    origin_df = get_raw_origin(plants_df).dropna()
    transformed_origin_df = transform_origin_data(origin_df)

    load_origins(transformed_origin_df)
