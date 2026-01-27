import os
import pymssql
from dotenv import load_dotenv

load_dotenv()

def get_rds_connection() -> pymssql.Connection:
    host = os.getenv('DB_HOST')
    port = int(os.getenv('DB_PORT', 1433))
    user = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')
    db = os.getenv('DB_NAME')

    conn: pymssql.Connection = pymssql.connect(server=host, port=port, user=user, password=password, database=db)
    return conn


def get_plant_id_mappings(conn: pymssql.Connection) -> dict:
    """Get plant name -> plant_id mapping dictionary"""
    pass

def get_origin_id_mappings(conn: pymssql.Connection) -> dict:
    """Get city_name -> origin_id mapping dictionary"""
    pass

def get_botanist_id_mappings(conn: pymssql.Connection) -> dict:
    """Get botanist name -> botanist_id mapping dictionary"""
    pass

def get_country_id_mappings(conn: pymssql.Connection) -> dict:
    """Get country name -> country id mapping dictionary"""
    pass

def load_to_plant_reading_table(conn: pymssql.Connection, data: dict) -> None:
    """
    Load plant reading to reading table:
    Example dict:
    data = {
        plant_id : int,
        soil_moisture : float,
        temperature : float,
        recording_taken : datetime.datetime
        last_watered : datetime.datetime
    }
    """
    pass

def load_to_plant_table(conn: pymssql.Connection, data: dict) -> None:
    """
    Load plant details to plant table:
    Example dict:
    data = {
        name : str,
        scientific_name : str,
        origin_id : int,
        botanist_id : int,
        image_license_url : Optional[int],
        image_url : Optional[int],
        thumbnail : Optional[int]
    }
    """
    pass

def load_to_origin_table(conn: pymssql.Connection, data: dict) -> None:
    """
    Load origin details to origin table:
    Example dict:
    data = {
        city : str,
        country_id : int,
        lat : float,
        long : float
    }
    """
    pass

def load_to_botanist_table(conn: pymssql.Connection, data: dict) -> None:
    """
    Load botanist details to botanist table:
    Example dict:
    data = {
        email : str,
        name : str,
        phone : str
    }
    """
    pass

def load_to_country_table(conn: pymssql.Connection, data: dict) -> None:
    """
    Load country details to country table:
    Example dict:
    data = {
        country_name : str
    }
    """
    pass

if __name__ == "__main__":
    conn = get_rds_connection()
    #Do some load tests
    conn.close()