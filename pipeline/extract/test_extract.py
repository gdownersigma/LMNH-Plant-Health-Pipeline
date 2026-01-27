from extract import fetch_plant, does_plant_exist, fetch_all_plants
import requests


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

        assert result is False


class TestFetchAllPlants:
    """Tests for the fetch_all_plants function."""

    def test_returns_list_of_plants(self, monkeypatch, sample_plant_data):
        """Should return a list of plant dictionaries."""
        plants = [sample_plant_data, sample_plant_data, None, None, None]
        monkeypatch.setattr(
            "extract.fetch_plant", lambda id: plants[id - 1] if id <= len(plants) else None)

        result = fetch_all_plants()

        assert isinstance(result, list)
        assert len(result) == 2

    def test_stops_after_consecutive_failures(self, mocker):
        """Should stop fetching after max consecutive failures."""
        mock_fetch = mocker.patch("extract.fetch_plant", return_value=None)

        fetch_all_plants(max_consecutive_failures=3)

        assert mock_fetch.call_count == 3

    def test_resets_failure_count_on_success(self, monkeypatch, sample_plant_data):
        """Should reset failure count when valid plant found."""
        responses = [None, None, sample_plant_data, None, None, None]
        monkeypatch.setattr(
            "extract.fetch_plant", lambda id: responses[id - 1] if id <= len(responses) else None)

        result = fetch_all_plants(max_consecutive_failures=3)

        assert len(result) == 1
