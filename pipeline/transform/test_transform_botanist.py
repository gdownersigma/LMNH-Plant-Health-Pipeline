"""Tests for transform_botanist.py."""
# pylint: disable=redefined-builtin
import pytest
from transform_botanist import clean_phone_number


class TestCleanBotanists:
    """Tests to clean botanist data."""

    @pytest.mark.parametrize("input, output", [
        ["1234567890", "123-456-7890"],
        ["(123)456-7890", "123-456-7890"],
        ["123.456.7890", "123-456-7890"],
        ["+1(123.456-7890", "+1-123-456-7890"],
        ["", None],
        [None, None],
        ["001-123.456-7890", "+1-123-456-7890"],
        ["101-123-456-7890", "+101-123-456-7890"],
        ["001-212-276-0013x63686", "+1-212-276-0013x63686"],
        ["44(212.276-0013x063", "+44-212-276-0013x063"],
    ])
    def test_clean_phone_number(self, input, output):
        """Should clean and standardise phone numbers."""
        assert clean_phone_number(input) == output
