"""Tests for the extract module."""
import requests
import pandas as pd
from extract import fetch_plant, does_plant_exist, fetch_all_plants, to_dataframe


class TestFetchPlant:
    """Tests for the fetch_plant function."""

    def test_fetch_plant_returns_correct_keys_for_valid_plant(self, monkeypatch, sample_plant_data):
        """Should return dictionary with all expected keys for valid plant."""
        def mock_get(url, timeout=None):
            response = requests.Response()
            response.status_code = 200
            response.json = lambda: sample_plant_data
            return response

        monkeypatch.setattr(requests, "get", mock_get)

        result = fetch_plant(1)

        assert "plant_id" in result
        assert "name" in result
        assert "botanist" in result
        assert "last_watered" in result
        assert "origin_location" in result
        assert "recording_taken" in result
        assert "soil_moisture" in result
        assert "temperature" in result

    def test_fetch_plant_returns_correct_keys_for_not_found(self, mock_plant_not_found):
        """Should return dictionary with error and plant_id keys when plant not found."""
        mock_plant_not_found(999)

        result = fetch_plant(999)

        assert "error" in result
        assert "plant_id" in result
        assert result["error"] == "plant not found"

    def test_fetch_plant_returns_correct_keys_for_sensor_fault(self, mock_sensor_fault):
        """Should return dictionary with error and plant_id keys when sensor fault."""
        mock_sensor_fault(23)

        result = fetch_plant(23)

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

    def test_returns_list_of_plants(self, monkeypatch, sample_plant_data):
        """Should return a list of plant dictionaries."""
        def mock_fetch(id):
            if id <= 2:
                return sample_plant_data
            return {"error": "plant not found", "plant_id": id}

        monkeypatch.setattr("extract.fetch_plant", mock_fetch)

        result = fetch_all_plants()

        assert isinstance(result, list)
        assert len(result) == 2

    def test_stops_after_consecutive_failures(self, mocker):
        """Should stop fetching after max consecutive failures."""
        mock_fetch = mocker.patch(
            "extract.fetch_plant",
            return_value={"error": "plant not found", "plant_id": 1}
        )

        fetch_all_plants(max_consecutive_failures=3)

        assert mock_fetch.call_count == 3

    def test_resets_failure_count_on_success(self, monkeypatch, sample_plant_data):
        """Should reset failure count when valid plant found."""
        def mock_fetch(id):
            if id == 3:
                return sample_plant_data
            return {"error": "plant not found", "plant_id": id}

        monkeypatch.setattr("extract.fetch_plant", mock_fetch)

        result = fetch_all_plants(max_consecutive_failures=3)

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
