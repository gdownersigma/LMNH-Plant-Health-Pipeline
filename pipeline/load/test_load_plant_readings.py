"""Tests for the load_plant_readings module."""
import pytest
import pandas as pd
from load_plant_readings import insert_plant_reading, load_plant_readings


class TestInsertPlantReading:
    """Tests for the insert_plant_reading function."""

    def test_calls_execute(self, mocker):
        """Should call cursor.execute."""
        mock_cursor = mocker.MagicMock()
        mock_conn = mocker.MagicMock()
        mock_conn.cursor.return_value.__enter__ = mocker.MagicMock(
            return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = mocker.MagicMock(
            return_value=False)

        row = {
            "plant_id": 1,
            "soil_moisture": 25.5,
            "temperature": 18.2,
            "recording_taken": "2026-01-27",
            "last_watered": "2026-01-26"
        }

        insert_plant_reading(mock_conn, row)

        mock_cursor.execute.assert_called_once()


class TestLoadPlantReadings:
    """Tests for the load_plant_readings function."""

    def test_commits_on_success(self, mocker):
        """Should commit when successful."""
        df = pd.DataFrame({
            'plant_id': [1],
            'soil_moisture': [25.5],
            'temperature': [18.2],
            'recording_taken': ['2026-01-27'],
            'last_watered': ['2026-01-26']
        })

        mock_conn = mocker.MagicMock()
        mocker.patch("load_plant_readings.get_connection",
                     return_value=mock_conn)
        mocker.patch("load_plant_readings.insert_plant_reading")

        load_plant_readings(df)

        mock_conn.commit.assert_called_once()

    def test_rollback_on_error(self, mocker):
        """Should rollback on error."""
        df = pd.DataFrame({
            'plant_id': [1],
            'soil_moisture': [25.5],
            'temperature': [18.2],
            'recording_taken': ['2026-01-27'],
            'last_watered': ['2026-01-26']
        })

        mock_conn = mocker.MagicMock()
        mocker.patch("load_plant_readings.get_connection",
                     return_value=mock_conn)
        mocker.patch("load_plant_readings.insert_plant_reading",
                     side_effect=Exception("error"))

        with pytest.raises(Exception):
            load_plant_readings(df)

        mock_conn.rollback.assert_called_once()
