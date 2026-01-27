"""Script to retrieve plant data from the API and save it as a dataframe."""
import pandas as pd


def fetch_plant(plant_id: int) -> dict:
    """Return a dictionary with plant data for the given plant ID."""
    pass


def does_plant_exist(plant: dict) -> bool:
    """Check if the plant actually exists in the API response."""
    pass


def fetch_all_plants(base_url: str, max_consecutive_failures: int = 3) -> list[dict]:
    """Fetch all plant data from the API, handling consecutive failures."""
    pass


def to_dataframe(plants: list[dict]) -> pd.DataFrame:
    """Convert a list of plant dictionaries to a pandas DataFrame."""
    pass


if __name__ == "__main__":
    pass
