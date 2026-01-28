import os
import pymssql
import csv
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    conn = pymssql.connect(server=os.getenv('DB_HOST'), port=int(os.getenv('DB_PORT', 1433)),
                          user=os.getenv('DB_USER'), password=os.getenv('DB_PASSWORD'),
                          database=os.getenv('DB_NAME'))
    cursor = conn.cursor()

    # Load data in order respecting foreign key constraints

    # 1. Load country data
    with open('dummy_tables/country.csv') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cursor.execute("INSERT INTO country (country_name) VALUES (%s)",
                         (row['country_name'],))
    print("Country data loaded.")

    # 2. Load city data
    with open('dummy_tables/city.csv') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cursor.execute("INSERT INTO city (city_name, country_id) VALUES (%s, %s)",
                         (row['city_name'], row['country_id']))
    print("City data loaded.")

    # 3. Load botanist data
    with open('dummy_tables/botanist.csv') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cursor.execute("INSERT INTO botanist (email, name, phone) VALUES (%s, %s, %s)",
                         (row['email'], row['name'], row['phone']))
    print("Botanist data loaded.")

    # 4. Load origin data
    with open('dummy_tables/origin.csv') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cursor.execute("INSERT INTO origin (city_id, lat, long) VALUES (%s, %s, %s)",
                         (row['city_id'], row['lat'], row['long']))
    print("Origin data loaded.")

    # 5. Load plant data
    with open('dummy_tables/plant.csv') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cursor.execute("""INSERT INTO plant (plant_id, name, scientific_name, origin_id, botanist_id,
                           image_license_url, image_url, thumbnail)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                         (row['plant_id'], row['name'], row['scientific_name'], row['origin_id'],
                          row['botanist_id'], row['image_license_url'], row['image_url'], row['thumbnail']))
    print("Plant data loaded.")

    # 6. Load plant_reading data
    with open('dummy_tables/plant_reading.csv') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cursor.execute("""INSERT INTO plant_reading (plant_id, soil_moisture, temperature,
                           recording_taken, last_watered) VALUES (%s, %s, %s, %s, %s)""",
                         (row['plant_id'], row['soil_moisture'], row['temperature'],
                          row['recording_taken'], row['last_watered']))
    print("Plant reading data loaded.")

    conn.commit()
    cursor.close()
    conn.close()
    print("\nAll dummy data loaded successfully.")
