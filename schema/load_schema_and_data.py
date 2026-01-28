import os
import pymssql
import csv
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    return pymssql.connect(server=os.getenv('DB_HOST'), port=int(os.getenv('DB_PORT', 1433)),
                           user=os.getenv('DB_USER'), password=os.getenv('DB_PASSWORD'),
                           database=os.getenv('DB_NAME'))


if __name__ == "__main__":
    conn = get_connection()
    with conn.cursor() as cursor:
        with open('schema.sql') as f:
            for stmt in f.read().split(';'):
                if stmt.strip():
                    cursor.execute(stmt)
                    conn.commit()

    with conn.cursor() as cursor:
        with open('seed_botanists.csv') as f:
            for row in csv.DictReader(f):
                cursor.execute("INSERT INTO botanist (email, name, phone) VALUES (%s, %s, %s)",
                               (row['botanist_email'], row['botanist_name'], row['botanist_phone']))
                conn.commit()

    with conn.cursor() as cursor:
        cursor.execute("SET IDENTITY_INSERT country ON")
        with open('countries.csv') as f:
            for row in csv.DictReader(f):
                cursor.execute("INSERT INTO country (country_name, country_id) VALUES (%s, %s)",
                               (row['origin_country'], row['country_id']))
                conn.commit()
        cursor.execute("SET IDENTITY_INSERT country OFF")
        conn.commit()

    with conn.cursor() as cursor:
        cursor.execute("SET IDENTITY_INSERT city ON")
        with open('cities.csv') as f:
            for row in csv.DictReader(f):
                cursor.execute("INSERT INTO city (city_name, city_id, country_id) VALUES (%s, %s, %s)",
                               (row['origin_city'], row['city_id'], row['country_id']))
                conn.commit()
        cursor.execute("SET IDENTITY_INSERT city OFF")
        conn.commit()

    conn.close()
    print("Schema and data loaded successfully.")
