"""Script to retrieve plant data from the API asynchronously."""
import asyncio
import aiohttp
import pandas as pd


async def fetch_plant(session: aiohttp.ClientSession, plant_id: int) -> dict:
    """Return a dictionary with plant data for the given plant ID."""
    url = f"https://tools.sigmalabs.co.uk/api/plants/{plant_id}"
    async with session.get(url) as response:
        return await response.json()


def does_plant_exist(plant: dict) -> bool:
    """Check if the plant actually exists in the API response."""
    error = plant.get("error", False)
    if error == "plant not found":
        return False
    if error == "plant sensor fault":
        print("Sensor fault detected.")
    elif error == "plant on loan to another museum":
        print("Plant on loan detected.")
    return True


async def fetch_all_plants(max_consecutive_failures: int = 5) -> list[dict]:
    """Fetch all plant data from the API, handling consecutive failures."""

    plants = []
    consecutive_failures = 0
    plant_id = 1
    batch_size = 30

    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
        while consecutive_failures < max_consecutive_failures:

            tasks = [
                fetch_plant(session, pid)
                for pid in range(plant_id, plant_id + batch_size)
            ]

            results = await asyncio.gather(*tasks)

            for i, plant in enumerate(results):
                current_id = plant_id + i

                if does_plant_exist(plant):
                    plants.append(plant)
                    print(f"Fetched plant ID {current_id}")
                    consecutive_failures = 0
                else:
                    print(f"Plant ID {current_id} not found.")
                    consecutive_failures += 1

                    if consecutive_failures >= max_consecutive_failures:
                        break

            plant_id += batch_size

    return plants


def to_dataframe(plants: list[dict]) -> pd.DataFrame:
    """Convert a list of plant dictionaries to a pandas DataFrame."""

    flattened = []
    for plant in plants:
        row = {
            "plant_id": plant.get("plant_id"),
            "name": plant.get("name"),
            "scientific_name": plant.get("scientific_name", [None])[0],
            "soil_moisture": plant.get("soil_moisture"),
            "temperature": plant.get("temperature"),
            "recording_taken": plant.get("recording_taken"),
            "last_watered": plant.get("last_watered"),
        }

        # Flatten botanist
        botanist = plant.get("botanist") or {}
        row["botanist_name"] = botanist.get("name")
        row["botanist_email"] = botanist.get("email")
        row["botanist_phone"] = botanist.get("phone")

        # Flatten origin_location
        location = plant.get("origin_location") or {}
        row["origin_city"] = location.get("city")
        row["origin_country"] = location.get("country")
        row["origin_latitude"] = location.get("latitude")
        row["origin_longitude"] = location.get("longitude")

        # Flatten images
        images = plant.get("images") or {}
        row["image_license_url"] = images.get("license_url")
        row["image_original_url"] = images.get("original_url")
        row["image_thumbnail"] = images.get("thumbnail")

        flattened.append(row)

    return pd.DataFrame(flattened)


if __name__ == "__main__":
    all_plants = asyncio.run(fetch_all_plants())
    df = to_dataframe(all_plants)
    df.to_csv("out.csv")
