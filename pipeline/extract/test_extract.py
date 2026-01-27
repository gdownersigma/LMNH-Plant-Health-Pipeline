from extract import fetch_plant
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
