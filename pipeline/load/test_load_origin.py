"""Tests for the load_origin module."""
import pytest
import pandas as pd
from load_origin import (
    get_country_id,
    get_city_id,
    create_country,
    create_city,
    get_or_create_country,
    get_or_create_city,
    insert_origin,
    load_origin,
    load_origins
)


class TestGetCountryId:
    """Tests for the get_country_id function."""

    def test_returns_id_when_found(self, mocker):
        """Should return country_id when country exists."""
        mock_cursor = mocker.MagicMock()
        mock_cursor.fetchone.return_value = (5,)
        mock_conn = mocker.MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        result = get_country_id(mock_conn, "United Kingdom")

        assert result == 5

    def test_returns_none_when_not_found(self, mocker):
        """Should return None when country doesn't exist."""
        mock_cursor = mocker.MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_conn = mocker.MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        result = get_country_id(mock_conn, "Atlantis")

        assert result is None


class TestGetCityId:
    """Tests for the get_city_id function."""

    def test_returns_id_when_found(self, mocker):
        """Should return city_id when city and country match."""
        mock_cursor = mocker.MagicMock()
        mock_cursor.fetchone.return_value = (10,)
        mock_conn = mocker.MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        result = get_city_id(mock_conn, "London", 5)

        assert result == 10

    def test_returns_none_when_not_found(self, mocker):
        """Should return None when city doesn't exist."""
        mock_cursor = mocker.MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_conn = mocker.MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        result = get_city_id(mock_conn, "Nowhere", 5)

        assert result is None


class TestCreateCountry:
    """Tests for the create_country function."""

    def test_inserts_country_and_returns_id(self, mocker):
        """Should insert country and return new country_id."""
        mock_cursor = mocker.MagicMock()
        mock_cursor.fetchone.return_value = (7,)
        mock_conn = mocker.MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        result = create_country(mock_conn, "France")

        assert result == 7
        assert mock_cursor.execute.call_count == 2


class TestCreateCity:
    """Tests for the create_city function."""

    def test_inserts_city_and_returns_id(self, mocker):
        """Should insert city and return new city_id."""
        mock_cursor = mocker.MagicMock()
        mock_cursor.fetchone.return_value = (15,)
        mock_conn = mocker.MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        result = create_city(mock_conn, "Paris", 7)

        assert result == 15
        assert mock_cursor.execute.call_count == 2


class TestGetOrCreateCountry:
    """Tests for the get_or_create_country function."""

    def test_returns_existing_id(self, mocker):
        """Should return existing ID when country exists."""
        mocker.patch("load_origin.get_country_id", return_value=3)
        mock_conn = mocker.MagicMock()

        result = get_or_create_country(mock_conn, "Germany")

        assert result == 3

    def test_creates_new_country(self, mocker):
        """Should create new country when doesn't exist."""
        mocker.patch("load_origin.get_country_id", return_value=None)
        mocker.patch("load_origin.create_country", return_value=8)
        mock_conn = mocker.MagicMock()

        result = get_or_create_country(mock_conn, "Spain")

        assert result == 8


class TestGetOrCreateCity:
    """Tests for the get_or_create_city function."""

    def test_returns_existing_id(self, mocker):
        """Should return existing ID when city exists."""
        mocker.patch("load_origin.get_city_id", return_value=20)
        mock_conn = mocker.MagicMock()

        result = get_or_create_city(mock_conn, "Berlin", 3)

        assert result == 20

    def test_creates_new_city(self, mocker):
        """Should create new city when doesn't exist."""
        mocker.patch("load_origin.get_city_id", return_value=None)
        mocker.patch("load_origin.create_city", return_value=25)
        mock_conn = mocker.MagicMock()

        result = get_or_create_city(mock_conn, "Madrid", 8)

        assert result == 25


class TestInsertOrigin:
    """Tests for the insert_origin function."""

    def test_inserts_origin_and_returns_id(self, mocker):
        """Should insert origin record and return origin_id."""
        mock_cursor = mocker.MagicMock()
        mock_cursor.fetchone.return_value = (100,)
        mock_conn = mocker.MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        result = insert_origin(mock_conn, 10, 51.5074, -0.1278)

        assert result == 100
        assert mock_cursor.execute.call_count == 2


class TestLoadOrigin:
    """Tests for the load_origin function."""

    def test_loads_origin_with_all_relationships(self, mocker):
        """Should create country, city, and origin."""
        mocker.patch("load_origin.get_or_create_country", return_value=5)
        mocker.patch("load_origin.get_or_create_city", return_value=10)
        mocker.patch("load_origin.insert_origin", return_value=100)
        mock_conn = mocker.MagicMock()

        row = {
            "origin_country": "United Kingdom",
            "origin_city": "London",
            "origin_latitude": 51.5074,
            "origin_longitude": -0.1278
        }

        result = load_origin(mock_conn, row)

        assert result == 100


class TestLoadOrigins:
    """Tests for the load_origins function."""

    def test_loads_all_origins(self, mocker):
        """Should load all origins from dataframe."""
        df = pd.DataFrame({
            'origin_country': ['UK', 'France'],
            'origin_city': ['London', 'Paris'],
            'origin_latitude': [51.5, 48.8],
            'origin_longitude': [-0.1, 2.3]
        })

        mock_conn = mocker.MagicMock()
        mocker.patch("load_origin.get_connection", return_value=mock_conn)
        mocker.patch("load_origin.load_origin", side_effect=[1, 2])

        load_origins(df)

        mock_conn.commit.assert_called_once()

    def test_rollback_on_error(self, mocker):
        """Should rollback on error."""
        df = pd.DataFrame({
            'origin_country': ['UK'],
            'origin_city': ['London'],
            'origin_latitude': [51.5],
            'origin_longitude': [-0.1]
        })

        mock_conn = mocker.MagicMock()
        mocker.patch("load_origin.get_connection", return_value=mock_conn)
        mocker.patch("load_origin.load_origin", side_effect=Exception("error"))

        with pytest.raises(Exception):
            load_origins(df)

        mock_conn.rollback.assert_called_once()
