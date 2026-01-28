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
    batch_size = 10

    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=25)) as session:
        while consecutive_failures < max_consecutive_failures:
            # Create tasks for a batch of plant IDs
            tasks = [
                fetch_plant(session, pid)
                for pid in range(plant_id, plant_id + batch_size)
            ]

            # Fetch batch concurrently
            results = await asyncio.gather(*tasks)

            # Process results in order to track consecutive failures
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


# To run the async function
if __name__ == "__main__":
    plants = asyncio.run(fetch_all_plants())
    df = pd.DataFrame(plants)
    print(f"Fetched {len(plants)} plants")
    df.to_csv("extracted_plants.csv", index=False)
