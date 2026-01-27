# pylint: disable=missing-function-docstring, missing-class-docstring, missing-module-docstring
"""Tests for transform_origin.py"""

import pytest
import pandas as pd

from transform_origin import (validate_latitude, validate_longitude, validate_city_country,
                              clean_city_country, clean_lat_long)


class TestValidateOriginData:
    """Tests to clean botanist data."""

    @pytest.mark.parametrize("data, output", [
        [10.0, True],
        [90.0, True],
        [-90.0, True],
        [91.0, False],
        [-91.0, False],
        [None, False],
        ["string", False],
        [0, True],
        [56398285, False],
        [67.77454747, True],
    ])
    def test_validate_latitude(self, data, output):
        assert validate_latitude(data) == output

    @pytest.mark.parametrize("data, output", [
        [10.0, True],
        [180.0, True],
        [-180.0, True],
        [181.0, False],
        [-181.0, False],
        [None, False],
        ["string", False],
        [0, True],
        [56398285, False],
        [67.77454747, True],
    ])
    def test_validate_longitude(self, data, output):
        assert validate_longitude(data) == output

    @pytest.mark.parametrize("data, output", [
        ["", False],
        ["   ", False],
        [180.0, False],
        ["Valid City", True],
        ["Valid Country", True],
        ["Triangle", True],
        [None, False],
        [12345, False],
    ])
    def test_validate_city_country(self, data, output):
        assert validate_city_country(data) == output


class TestCleanOriginData:
    """Tests to clean origin data."""

    @pytest.mark.parametrize("data, output", [
        [{'origin_city': "Lisbon", 'origin_country': "portugal"},
         {'city': "Lisbon", 'country': "Portugal"}],
        [{'origin_city': "Madrid", 'origin_country': "Spain"},
         {'city': "Madrid", 'country': "Spain"}],
        [{'origin_city': " New York ", 'origin_country': " USA "},
         {'city': "New York", 'country': "Usa"}],
        [{'origin_city': "london ", 'origin_country': " united kingdom"},
         {'city': "London", 'country': "United Kingdom"}]
    ])
    def test_clean_city_country(self, data, output):
        assert clean_city_country(pd.DataFrame([data]))[
            'origin_city'].iloc[0] == output['city']
        assert clean_city_country(pd.DataFrame([data]))[
            'origin_country'].iloc[0] == output['country']

    @pytest.mark.parametrize("data, output", [
        [{'origin_latitude': "45.0", 'origin_longitude': "-93.0"},
         {'origin_latitude': 45.0, 'origin_longitude': -93.0}],
        [{'origin_latitude': "90.0", 'origin_longitude': "180.0"},
         {'origin_latitude': 90.0, 'origin_longitude': 180.0}],
        [{'origin_latitude': "-90", 'origin_longitude': "-180"},
         {'origin_latitude': -90.0, 'origin_longitude': -180.0}],
        [{'origin_latitude': "67.77454747", 'origin_longitude': "-122.4194155"},
         {'origin_latitude': 67.77454747, 'origin_longitude': -122.4194155}],
    ])
    def test_clean_lat_long(self, data, output):
        cleaned_df = clean_lat_long(pd.DataFrame([data]))
        assert cleaned_df['origin_latitude'].iloc[0] == output['origin_latitude']
        assert cleaned_df['origin_longitude'].iloc[0] == output['origin_longitude']
