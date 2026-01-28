"""The code to run the ETL pipeline."""
import pandas as pd
import asyncio

# Extract
from extract.extract import fetch_all_plants, to_dataframe

# Transform
from transform.transform_origin import get_raw_origin, transform_origin_data
from transform.transform_botanist import get_botanists
from transform.transform_plants import transform_plant_data
from transform.transform_readings import transform_plant_readings

# Load
from load.load_origin import get_connection, load_origin
from load.load_botanist import load_botanists
from load.load_plant import load_plants
from load.load_plant_readings import load_plant_readings


def extract() -> pd.DataFrame:
    """Extract all plant data from API into a DataFrame."""
    print("=== EXTRACT PHASE ===")
    all_plants = asyncio.run(fetch_all_plants())
    plants_df = to_dataframe(all_plants)
    print(f"Extracted {len(plants_df)} plants")
    return plants_df


def transform(plants_df: pd.DataFrame) -> dict:
    """Transform and clean all plant data.

    Returns a dict containing all transformed DataFrames.
    """
    print("\n=== TRANSFORM PHASE ===")

    # Transform origin data (unique origins only)
    origin_df = get_raw_origin(plants_df).dropna().drop_duplicates()
    origin_df = transform_origin_data(origin_df)
    print(f"Transformed {len(origin_df)} unique origin records")

    # Transform botanist data
    botanist_df = get_botanists(plants_df)
    print(f"Transformed {len(botanist_df)} botanist records")

    # Transform plant data
    plant_df = transform_plant_data(plants_df)
    print(f"Transformed {len(plant_df)} plant records")

    # Transform plant readings data
    readings_df = transform_plant_readings(plants_df)
    print(f"Transformed {len(readings_df)} reading records")

    return {
        "origin": origin_df,
        "botanist": botanist_df,
        "plant": plant_df,
        "readings": readings_df,
        "full": plants_df  # Keep full df for cross-referencing
    }


def load(transformed_data: dict) -> None:
    """Load all transformed data into the database.

    Order of loading respects foreign key constraints:
    1. country (created via origin load)
    2. city (created via origin load)  
    3. origin
    4. botanist
    5. plant (references origin_id and botanist_id)
    6. plant_reading (references plant_id)
    """
    print("\n=== LOAD PHASE ===")

    origin_df = transformed_data["origin"]
    botanist_df = transformed_data["botanist"]
    plant_df = transformed_data["plant"]
    readings_df = transformed_data["readings"]

    # 1. Load origins (also creates countries and cities)
    print("Loading origins (with countries and cities)...")
    conn = get_connection()
    try:
        for _, row in origin_df.iterrows():
            load_origin(conn, row)
        conn.commit()
    finally:
        conn.close()
    print(f"  Loaded {len(origin_df)} unique origins")

    # 2. Load botanists
    print("Loading botanists...")
    botanist_email_to_id = load_botanists(botanist_df)
    print(f"  Loaded {len(botanist_email_to_id)} unique botanists")

    # 3. Load plants (looks up origin_id from DB directly)
    print("Loading plants...")
    load_plants(plant_df, botanist_email_to_id)
    print(f"  Loaded {len(plant_df)} plants")

    # 4. Load plant readings
    print("Loading plant readings...")
    load_plant_readings(readings_df)
    print(f"  Loaded {len(readings_df)} plant readings")

    print("\n=== PIPELINE COMPLETE ===")


def run_pipeline() -> None:
    """Run the full ETL pipeline."""
    # Extract
    plants_df = extract()

    # Transform
    transformed_data = transform(plants_df)

    # Load
    load(transformed_data)


if __name__ == "__main__":
    run_pipeline()
