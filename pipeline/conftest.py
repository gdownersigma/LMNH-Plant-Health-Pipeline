import pytest
import requests
import pandas as pd


@pytest.fixture
def mock_plant_not_found(monkeypatch):
    """Fixture that mocks a plant not found response."""
    def _mock(plant_id):
        def mock_get(url, timeout=None):
            response = requests.Response()
            response.status_code = 200
            response.json = lambda: {
                "error": "plant not found", "plant_id": plant_id}
            return response
        monkeypatch.setattr(requests, "get", mock_get)
    return _mock


@pytest.fixture
def mock_sensor_fault(monkeypatch):
    """Fixture that mocks a plant sensor fault response."""
    def _mock(plant_id):
        def mock_get(url, timeout=None):
            response = requests.Response()
            response.status_code = 200
            response.json = lambda: {
                "error": "plant sensor fault", "plant_id": plant_id}
            return response
        monkeypatch.setattr(requests, "get", mock_get)
    return _mock


@pytest.fixture
def sample_plant_data():
    """Sample plant data for testing."""
    return {
        "botanist": {
            "email": "sherry.campbell@lnhm.co.uk",
            "name": "Sherry Campbell",
            "phone": "+1-662-659-8097x8928"
        },
        "last_watered": "2026-01-26T13:12:19",
        "name": "Venus flytrap",
        "origin_location": {
            "city": "Mitchellfurt",
            "country": "Suriname",
            "latitude": "81.2003535",
            "longitude": "7.815683"
        },
        "plant_id": 1,
        "recording_taken": "2026-01-27T10:08:05.308991",
        "soil_moisture": 28.58,
        "temperature": 16.91
    }


@pytest.fixture
def sample_plant_data_extended():
    """Sample plant data for testing."""
    return {
        "botanist": {
            "email": "sherry.campbell@lnhm.co.uk",
            "name": "Sherry Campbell",
            "phone": "+1-662-659-8097x8928"
        },
        "images": {
            "license": 4,
            "license_name": "Attribution License",
            "medium_url": "https://example.com/image.jpg"
        },
        "last_watered": "2026-01-26T13:12:19",
        "name": "Venus flytrap",
        "origin_location": {
            "city": "Mitchellfurt",
            "country": "Suriname",
            "latitude": "81.2003535",
            "longitude": "7.815683"
        },
        "plant_id": 1,
        "recording_taken": "2026-01-27T10:08:05.308991",
        "scientific_name": ["Dionaea muscipula"],
        "soil_moisture": 28.58,
        "temperature": 16.91
    }


@pytest.fixture
def valid_readings_data():
    """Sample plant data for testing."""
    data = {
        "last_watered": "2026-01-26T13:12:19",
        "name": "Venus flytrap",
        "plant_id": 1,
        "recording_taken": "2026-01-27T10:08:05.308991",
        "soil_moisture": 28.58,
        "temperature": 16.91
    }
    data_frame = pd.json_normalize(data)
    return data_frame


@pytest.fixture
def invalid_readings_data():
    """Sample plant data for testing."""
    data = {
        "last_watered": "2026-01-26T13:12:19",
        "name": "Venus flytrap",
        "plant_id": 1,
        "recording_taken": "2026-01-27T10:08:05.308991",
        "soil_moisture": 28.58,
        "temperature": 16.91
    }
    data_frame = pd.json_normalize(data)
    return data_frame
