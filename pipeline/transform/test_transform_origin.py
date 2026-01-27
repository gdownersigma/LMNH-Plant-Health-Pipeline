"""Tests for transform_origin.py"""

import pytest
import pandas as pd

from transform_origin import (validate_latitude, validate_longitude, validate_city_country,
                              clean_city_country, clean_lat_long)

class TestValidateOriginData:
    """Tests to clean botanist data."""

    @pytest.mark.parametrize("input, output", [
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
    def test_validate_latitude(self, input, output):
        assert validate_latitude(input) == output
    
    @pytest.mark.parametrize("input, output", [
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
    def test_validate_longitude(self, input, output):
        assert validate_longitude(input) == output

    @pytest.mark.parametrize("input, output", [
        ["", False],
        ["   ", False],
        [180.0, False],
        ["Valid City", True],
        ["Valid Country", True],
        ["Triangle", True],
        [None, False],
        [12345, False],
    ])
    def test_validate_city_country(self, input, output):
        assert validate_city_country(input) == output

class TestCleanOriginData:
    """Tests to clean origin data."""

    @pytest.mark.parametrize("input, output", [
        [{'origin_city': "Lisbon", 'origin_country': "portugal"},
         {'origin_city': "Lisbon", 'origin_country': "Portugal"}],
        [{'origin_city': "Madrid", 'origin_country': "Spain"},
         {'origin_city': "Madrid", 'origin_country': "Spain"}],
        [{'origin_city': " New York ", 'origin_country': " USA "}, 
         {'origin_city': "New York", 'origin_country': "Usa"}],
        [{'origin_city': "london ", 'origin_country': " united kingdom"}, 
         {'origin_city': "London", 'origin_country': "United Kingdom"}]
    ])
    def test_clean_city_country(self, input, output):
        assert clean_city_country(pd.DataFrame([input]))['origin_city'].iloc[0] == output['origin_city']
        assert clean_city_country(pd.DataFrame([input]))['origin_country'].iloc[0] == output['origin_country']

    @pytest.mark.parametrize("input, output", [
        [{'origin_latitude': "45.0", 'origin_longitude': "-93.0"},
         {'origin_latitude': 45.0, 'origin_longitude': -93.0}],
        [{'origin_latitude': "90.0", 'origin_longitude': "180.0"},
         {'origin_latitude': 90.0, 'origin_longitude': 180.0}],
        [{'origin_latitude': "-90", 'origin_longitude': "-180"},
         {'origin_latitude': -90.0, 'origin_longitude': -180.0}],
        [{'origin_latitude': "67.77454747", 'origin_longitude': "-122.4194155"},
         {'origin_latitude': 67.77454747, 'origin_longitude': -122.4194155}],
    ])
    def test_clean_lat_long(self, input, output):
        cleaned_df = clean_lat_long(pd.DataFrame([input]))
        assert cleaned_df['origin_latitude'].iloc[0] == output['origin_latitude']
        assert cleaned_df['origin_longitude'].iloc[0] == output['origin_longitude']