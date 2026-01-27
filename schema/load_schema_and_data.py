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

    with open('schema.sql') as f:
        for stmt in f.read().split(';'):
            if stmt.strip():
                cursor.execute(stmt)

    with open('seed_botanists.csv') as f:
        for row in csv.DictReader(f):
            cursor.execute("INSERT INTO botanist (email, name, phone) VALUES (%s, %s, %s)",
                         (row['botanist_email'], row['botanist_name'], row['botanist_phone']))

    conn.commit()
    cursor.close()
    conn.close()
    print("Schema and data loaded successfully.")
