"""Pytest configuration and fixtures for rds_s3_pipeline tests."""
import pytest
import pandas as pd
from datetime import datetime, timedelta


@pytest.fixture
def sample_raw_data():
    """Fixture providing sample raw plant reading data."""
    base_date = datetime(2026, 1, 28)
    
    data = {
        'reading_date': [base_date] * 5 + [base_date - timedelta(days=1)] * 3,
        'plant_id': [1, 1, 1, 2, 2, 1, 1, 2],
        'plant_name': ['Venus Flytrap'] * 3 + ['Cactus'] * 2 + ['Venus Flytrap'] * 2 + ['Cactus'],
        'scientific_name': ['Dionaea muscipula'] * 3 + ['Mammillaria elongata'] * 2 + 
                          ['Dionaea muscipula'] * 2 + ['Mammillaria elongata'],
        'botanist_name': ['John Smith'] * 5 + ['John Smith'] * 3,
        'botanist_email': ['john.smith@lmnh.org'] * 8,
        'botanist_phone': ['+44-123-456-7890'] * 8,
        'temperature': [22.5, 21.8, 23.1, 25.0, 24.5, 20.5, 21.0, 24.0],
        'soil_moisture': [45.0, 42.0, 48.0, 30.0, 28.0, 40.0, 43.0, 32.0],
        'last_watered': [
            base_date - timedelta(hours=2),
            base_date - timedelta(hours=2),
            base_date - timedelta(hours=2),
            base_date - timedelta(hours=3),
            base_date - timedelta(hours=3),
            base_date - timedelta(days=1, hours=2),
            base_date - timedelta(days=1, hours=2),
            base_date - timedelta(days=1, hours=3)
        ]
    }
    
    return pd.DataFrame(data)


@pytest.fixture
def empty_dataframe():
    """Fixture providing an empty DataFrame with correct columns."""
    return pd.DataFrame(columns=[
        'reading_date', 'plant_id', 'plant_name', 'scientific_name',
        'botanist_name', 'botanist_email', 'botanist_phone',
        'temperature', 'soil_moisture', 'last_watered'
    ])


@pytest.fixture
def single_reading_data():
    """Fixture providing data with a single reading per plant per day."""
    base_date = datetime(2026, 1, 28)
    
    data = {
        'reading_date': [base_date, base_date],
        'plant_id': [1, 2],
        'plant_name': ['Venus Flytrap', 'Cactus'],
        'scientific_name': ['Dionaea muscipula', 'Mammillaria elongata'],
        'botanist_name': ['John Smith', 'Sarah Jones'],
        'botanist_email': ['john.smith@lmnh.org', 'sarah.jones@lmnh.org'],
        'botanist_phone': ['+44-123-456-7890', '+44-234-567-8901'],
        'temperature': [22.0, 25.0],
        'soil_moisture': [45.0, 30.0],
        'last_watered': [base_date - timedelta(hours=2), base_date - timedelta(hours=3)]
    }
    
    return pd.DataFrame(data)


@pytest.fixture
def extreme_values_data():
    """Fixture with extreme temperature and humidity values."""
    base_date = datetime(2026, 1, 28)
    
    data = {
        'reading_date': [base_date] * 4,
        'plant_id': [1, 1, 1, 1],
        'plant_name': ['Test Plant'] * 4,
        'scientific_name': ['Test species'] * 4,
        'botanist_name': ['Test Botanist'] * 4,
        'botanist_email': ['test@lmnh.org'] * 4,
        'botanist_phone': ['+44-000-000-0000'] * 4,
        'temperature': [10.0, 15.0, 25.0, 40.0],  # Wide range
        'soil_moisture': [0.0, 25.0, 75.0, 100.0],  # Full range
        'last_watered': [
            base_date - timedelta(hours=i) for i in range(4)
        ]
    }
    
    return pd.DataFrame(data)
