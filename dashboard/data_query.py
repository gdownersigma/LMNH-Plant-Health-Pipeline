"""File to query the database and S3 for the dashboard."""

from os import environ as ENV, _Environ
from dotenv import load_dotenv
import pandas as pd
from pymssql import connect, Connection


def get_db_connection(config: _Environ) -> Connection:
    """Create and return a database connection"""
    return connect(
        server=config['DB_HOST'],
        port=int(config['DB_PORT']),
        user=config['DB_USER'],
        password=config['DB_PASSWORD'],
        database=config['DB_NAME']
    )


def read_table_to_dataframe(conn: Connection, table_name: str) -> pd.DataFrame:
    """Read table into a pandas DataFrame"""
    with conn.cursor() as cur:
        cur.execute(f"SELECT * FROM {table_name}")
        columns = [desc[0] for desc in cur.description]
        data = cur.fetchall()

    return pd.DataFrame(data, columns=columns)


def get_key_metrics(conn: Connection) -> pd.DataFrame:
    """Returns all data from Database as a DataFrame."""
    with conn.cursor() as cur:
        cur.execute(
            f"""SELECT
                    p.plant_id,
                    p.name AS plant_name,
                    b.botanist_id,
                    b.name AS botanist_name,
                    cn.country_id,
                    cn.country_name
                FROM plant AS p 
                JOIN botanist AS b
                    ON p.botanist_id = b.botanist_id
                JOIN origin AS o
                    ON p.origin_id = o.origin_id
                JOIN city AS c
                    ON o.city_id = c.city_id
                JOIN country AS cn
                    ON c.country_id = cn.country_id;""")
        columns = [desc[0] for desc in cur.description]
        data = cur.fetchall()

    df = pd.DataFrame(data, columns=columns)
    return df


if __name__ == "__main__":

    load_dotenv()

    conn = get_db_connection(ENV)

    df = read_table_to_dataframe(conn, 'plant')

    print(df.head())

    conn.close()
