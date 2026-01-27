"""Tests for transform_origin.py"""

import pytest

from transform_origin import (validate_latitude, validate_longitude, validate_city_country)

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