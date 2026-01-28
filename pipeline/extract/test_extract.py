""""Tests for the extract module."""
import pytest
import pandas as pd
from unittest.mock import AsyncMock, MagicMock
from extract import fetch_plant, does_plant_exist, fetch_all_plants, to_dataframe


""""Tests for the extract module."""


class MockSession:
    """Mock aiohttp response and session."""

    def __init__(self, data):
        self.data = data

    def get(self, url):
        return self

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def json(self):
        return self.data


class TestFetchPlant:
    """Tests for the fetch_plant function."""

    @pytest.mark.asyncio
    async def test_fetch_plant_returns_correct_keys_for_valid_plant(self, sample_plant_data):
        """Should return dictionary with all expected keys for valid plant."""
        session = MockSession(sample_plant_data)
        result = await fetch_plant(session, 1)

        assert "plant_id" in result
        assert "name" in result
        assert "botanist" in result
        assert "last_watered" in result
        assert "origin_location" in result
        assert "recording_taken" in result
        assert "soil_moisture" in result
        assert "temperature" in result

    @pytest.mark.asyncio
    async def test_fetch_plant_returns_correct_keys_for_not_found(self):
        """Should return dictionary with error and plant_id keys when plant not found."""
        error_data = {"error": "plant not found", "plant_id": 999}
        session = MockSession(error_data)
        result = await fetch_plant(session, 999)

        assert "error" in result
        assert "plant_id" in result
        assert result["error"] == "plant not found"

    @pytest.mark.asyncio
    async def test_fetch_plant_returns_correct_keys_for_sensor_fault(self):
        """Should return dictionary with error and plant_id keys when sensor fault."""
        error_data = {"error": "plant sensor fault", "plant_id": 23}
        session = MockSession(error_data)
        result = await fetch_plant(session, 23)

        assert "error" in result
        assert "plant_id" in result
        assert result["error"] == "plant sensor fault"


class TestDoesPlantExist:
    """Tests for the does_plant_exist function."""

    def test_returns_true_for_valid_plant(self, sample_plant_data):
        """Should return True when plant data has no error key."""
        result = does_plant_exist(sample_plant_data)

        assert result is True

    def test_returns_false_for_plant_not_found(self):
        """Should return False when plant not found."""
        plant = {"error": "plant not found", "plant_id": 16998565}

        result = does_plant_exist(plant)

        assert result is False

    def test_returns_false_for_sensor_fault(self):
        """Should return False when sensor fault."""
        plant = {"error": "plant sensor fault", "plant_id": 23}

        result = does_plant_exist(plant)

        assert result is True


class TestFetchAllPlants:
    """Tests for the fetch_all_plants function."""

    @pytest.mark.asyncio
    async def test_returns_list_of_plants(self, monkeypatch, sample_plant_data):
        """Should return a list of plant dictionaries."""
        async def mock_fetch(session, plant_id):
            if plant_id <= 2:
                return sample_plant_data
            return {"error": "plant not found", "plant_id": plant_id}

        monkeypatch.setattr("extract.fetch_plant", mock_fetch)

        result = await fetch_all_plants()

        assert isinstance(result, list)
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_stops_after_consecutive_failures(self, monkeypatch):
        """Should stop fetching after max consecutive failures."""
        async def mock_fetch(session, plant_id):
            return {"error": "plant not found", "plant_id": plant_id}

        monkeypatch.setattr("extract.fetch_plant", mock_fetch)

        result = await fetch_all_plants(max_consecutive_failures=3)

        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_resets_failure_count_on_success(self, monkeypatch, sample_plant_data):
        """Should reset failure count when valid plant found."""
        async def mock_fetch(session, plant_id):
            if plant_id == 3:
                return sample_plant_data
            return {"error": "plant not found", "plant_id": plant_id}

        monkeypatch.setattr("extract.fetch_plant", mock_fetch)

        result = await fetch_all_plants(max_consecutive_failures=3)

        assert len(result) == 1


class TestToDataframe:
    """Tests for the to_dataframe function."""

    def test_returns_dataframe(self, sample_plant_data):
        """Should return a pandas DataFrame."""
        result = to_dataframe([sample_plant_data])

        assert isinstance(result, pd.DataFrame)

    def test_dataframe_has_correct_row_count(self, sample_plant_data_extended):
        """Should have one row per plant."""
        plants = [sample_plant_data_extended,
                  sample_plant_data_extended.copy()]
        plants[1]["plant_id"] = 2

        result = to_dataframe(plants)

        assert len(result) == 2

    def test_dataframe_handles_empty_list(self):
        """Should return empty DataFrame when given empty list."""
        result = to_dataframe([])

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0

    def test_dataframe_has_plant_columns(self, sample_plant_data_extended):
        """Should have top-level plant columns."""
        result = to_dataframe([sample_plant_data_extended])

        assert "plant_id" in result.columns
        assert "name" in result.columns
        assert "soil_moisture" in result.columns
        assert "temperature" in result.columns
        assert "recording_taken" in result.columns
        assert "last_watered" in result.columns

    def test_dataframe_has_botanist_columns(self, sample_plant_data_extended):
        """Should have flattened botanist columns."""
        result = to_dataframe([sample_plant_data_extended])

        assert "botanist_name" in result.columns
        assert "botanist_email" in result.columns
        assert "botanist_phone" in result.columns

    def test_dataframe_has_location_columns(self, sample_plant_data_extended):
        """Should have flattened origin_location columns."""
        result = to_dataframe([sample_plant_data_extended])

        assert "origin_city" in result.columns
        assert "origin_country" in result.columns
        assert "origin_latitude" in result.columns
        assert "origin_longitude" in result.columns

    def test_dataframe_botanist_values_correct(self, sample_plant_data_extended):
        """Should have correct botanist values."""
        result = to_dataframe([sample_plant_data_extended])

        assert result["botanist_name"].iloc[0] == "Sherry Campbell"
        assert result["botanist_email"].iloc[0] == "sherry.campbell@lnhm.co.uk"

    def test_dataframe_location_values_correct(self, sample_plant_data_extended):
        """Should have correct location values."""
        result = to_dataframe([sample_plant_data_extended])

        assert result["origin_city"].iloc[0] == "Mitchellfurt"
        assert result["origin_country"].iloc[0] == "Suriname"
