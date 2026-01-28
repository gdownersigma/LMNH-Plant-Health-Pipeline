"""Tests for the load_plant module."""
import pytest
import pandas as pd
from load_plant import (
    get_origin_id,
    get_plant_by_id,
    create_plant,
    update_plant,
    load_plant,
    load_plants,
    nan_to_none
)


class TestNanToNone:
    """Tests for the nan_to_none function."""

    def test_converts_nan_to_none(self):
        """Should convert NaN to None."""
        assert nan_to_none(float('nan')) is None

    def test_preserves_valid_values(self):
        """Should preserve non-NaN values."""
        assert nan_to_none("text") == "text"
        assert nan_to_none(42) == 42


class TestGetOriginId:
    """Tests for the get_origin_id function."""

    def test_returns_id_when_found(self, mocker):
        """Should return origin_id when coordinates match."""
        mock_cursor = mocker.MagicMock()
        mock_cursor.fetchone.return_value = (5,)
        mock_conn = mocker.MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        result = get_origin_id(mock_conn, 51.5074, -0.1278)

        assert result == 5

    def test_returns_none_when_not_found(self, mocker):
        """Should return None when coordinates don't exist."""
        mock_cursor = mocker.MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_conn = mocker.MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        result = get_origin_id(mock_conn, 99.999, 99.999)

        assert result is None


class TestGetPlantById:
    """Tests for the get_plant_by_id function."""

    def test_returns_id_when_found(self, mocker):
        """Should return plant_id when it exists."""
        mock_cursor = mocker.MagicMock()
        mock_cursor.fetchone.return_value = (10,)
        mock_conn = mocker.MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        result = get_plant_by_id(mock_conn, 10)

        assert result == 10

    def test_returns_none_when_not_found(self, mocker):
        """Should return None when plant doesn't exist."""
        mock_cursor = mocker.MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_conn = mocker.MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        result = get_plant_by_id(mock_conn, 999)

        assert result is None


class TestCreatePlant:
    """Tests for the create_plant function."""

    def test_inserts_plant_and_returns_id(self, mocker):
        """Should insert plant and return plant_id."""
        mock_cursor = mocker.MagicMock()
        mock_conn = mocker.MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        result = create_plant(
            mock_conn, 1, "Rose", "Rosa", 5, 3,
            "http://license.com", "http://image.com", "http://thumb.com"
        )

        assert result == 1
        mock_cursor.execute.assert_called_once()


class TestUpdatePlant:
    """Tests for the update_plant function."""

    def test_updates_plant_and_returns_id(self, mocker):
        """Should update plant and return plant_id."""
        mock_cursor = mocker.MagicMock()
        mock_conn = mocker.MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        result = update_plant(
            mock_conn, 1, "Sunflower", "Helianthus", 7, 2,
            None, None, None
        )

        assert result == 1
        mock_cursor.execute.assert_called_once()


class TestLoadPlant:
    """Tests for the load_plant function."""

    def test_creates_new_plant(self, mocker):
        """Should create plant when it doesn't exist."""
        mocker.patch("load_plant.get_plant_by_id", return_value=None)
        mock_create = mocker.patch("load_plant.create_plant", return_value=5)
        mock_conn = mocker.MagicMock()

        row = {
            "plant_id": 5,
            "name": "Cactus",
            "scientific_name": "Cactaceae",
            "image_license_url": None,
            "image_original_url": None,
            "image_thumbnail": None
        }

        result = load_plant(mock_conn, row, botanist_id=2, origin_id=8)

        assert result == 5
        mock_create.assert_called_once()

    def test_updates_existing_plant(self, mocker):
        """Should update plant when it exists."""
        mocker.patch("load_plant.get_plant_by_id", return_value=5)
        mock_update = mocker.patch("load_plant.update_plant", return_value=5)
        mock_conn = mocker.MagicMock()

        row = {
            "plant_id": 5,
            "name": "Updated Cactus",
            "scientific_name": "Cactaceae",
            "image_license_url": None,
            "image_original_url": None,
            "image_thumbnail": None
        }

        result = load_plant(mock_conn, row, botanist_id=2, origin_id=8)

        assert result == 5
        mock_update.assert_called_once()


class TestLoadPlants:
    """Tests for the load_plants function."""

    def test_loads_all_plants(self, mocker):
        """Should load all plants from dataframe."""
        df = pd.DataFrame({
            'plant_id': [1, 2],
            'name': ['Rose', 'Tulip'],
            'scientific_name': ['Rosa', 'Tulipa'],
            'botanist_email': ['alice@test.com', 'bob@test.com'],
            'origin_latitude': [51.5, 52.3],
            'origin_longitude': [-0.1, 1.2],
            'image_license_url': [None, None],
            'image_original_url': [None, None],
            'image_thumbnail': [None, None]
        })

        botanist_map = {'alice@test.com': 10, 'bob@test.com': 20}

        mock_conn = mocker.MagicMock()
        mocker.patch("load_plant.get_connection", return_value=mock_conn)
        mocker.patch("load_plant.get_origin_id", side_effect=[5, 6])
        mocker.patch("load_plant.load_plant")

        load_plants(df, botanist_map)

        mock_conn.commit.assert_called_once()

    def test_rollback_on_error(self, mocker):
        """Should rollback on error."""
        df = pd.DataFrame({
            'plant_id': [1],
            'name': ['Rose'],
            'scientific_name': ['Rosa'],
            'botanist_email': ['alice@test.com'],
            'origin_latitude': [51.5],
            'origin_longitude': [-0.1],
            'image_license_url': [None],
            'image_original_url': [None],
            'image_thumbnail': [None]
        })

        botanist_map = {'alice@test.com': 10}

        mock_conn = mocker.MagicMock()
        mocker.patch("load_plant.get_connection", return_value=mock_conn)
        mocker.patch("load_plant.get_origin_id", return_value=5)
        mocker.patch("load_plant.load_plant", side_effect=Exception("error"))

        with pytest.raises(Exception):
            load_plants(df, botanist_map)

        mock_conn.rollback.assert_called_once()
