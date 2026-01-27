"""Script to retrieve plant data from the API and save it as a dataframe."""
import pandas as pd
import requests


def fetch_plant(plant_id: int) -> dict:
    """Return a dictionary with plant data for the given plant ID."""
    response = requests.get(
        f"https://tools.sigmalabs.co.uk/api/plants/{plant_id}", timeout=5)
    return response.json()


def does_plant_exist(plant: dict) -> bool:
    """Check if the plant actually exists in the API response."""
    if plant.get("error", False):
        return False

    return True


def fetch_all_plants(max_consecutive_failures: int = 3) -> list[dict]:
    """Fetch all plant data from the API, handling consecutive failures."""
    pass


def to_dataframe(plants: list[dict]) -> pd.DataFrame:
    """Convert a list of plant dictionaries to a pandas DataFrame."""
    pass


if __name__ == "__main__":
    pass
