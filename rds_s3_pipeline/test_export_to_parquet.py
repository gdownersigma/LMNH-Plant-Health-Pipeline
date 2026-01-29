"""Tests for export_to_parquet module."""
import pytest
import pandas as pd
from datetime import datetime
from export_to_parquet import calculate_daily_summary


class TestCalculateDailySummary:
    """Tests for calculate_daily_summary function."""

    def test_basic_aggregation(self, sample_raw_data):
        """Test that basic aggregations are calculated correctly."""
        result = calculate_daily_summary(sample_raw_data)

        # Check shape - should have 3 rows (2 plants on day 1, 2 plants on day 2)
        # But data has plant 1 on 2 days, plant 2 on 2 days = 4 combinations
        assert not result.empty
        assert len(result) > 0

        # Check all expected columns exist
        expected_cols = [
            'reading_date', 'plant_id', 'plant_name', 'scientific_name',
            'botanist_name', 'botanist_email', 'botanist_phone',
            'min_temperature', 'max_temperature', 'avg_temperature',
            'median_temperature', 'percentile_25_temperature', 'percentile_75_temperature',
            'min_humidity', 'max_humidity', 'avg_humidity',
            'median_humidity', 'percentile_25_humidity', 'percentile_75_humidity',
            'times_watered'
        ]
        for col in expected_cols:
            assert col in result.columns, f"Missing column: {col}"

    def test_temperature_statistics(self, sample_raw_data):
        """Test that temperature statistics are calculated correctly."""
        result = calculate_daily_summary(sample_raw_data)

        # Get first row (most recent date, plant 1)
        first_row = result.iloc[0]

        # Check min/max are within expected bounds
        assert first_row['min_temperature'] <= first_row['avg_temperature']
        assert first_row['max_temperature'] >= first_row['avg_temperature']

        # Check percentiles are ordered correctly
        assert first_row['percentile_25_temperature'] <= first_row['median_temperature']
        assert first_row['median_temperature'] <= first_row['percentile_75_temperature']

        # Check all values are numeric
        assert pd.api.types.is_numeric_dtype(result['min_temperature'])
        assert pd.api.types.is_numeric_dtype(result['avg_temperature'])

    def test_humidity_statistics(self, sample_raw_data):
        """Test that humidity statistics are calculated correctly."""
        result = calculate_daily_summary(sample_raw_data)

        first_row = result.iloc[0]

        # Check min/max bounds
        assert first_row['min_humidity'] <= first_row['avg_humidity']
        assert first_row['max_humidity'] >= first_row['avg_humidity']

        # Check percentiles are ordered
        assert first_row['percentile_25_humidity'] <= first_row['median_humidity']
        assert first_row['median_humidity'] <= first_row['percentile_75_humidity']

    def test_watering_count(self, sample_raw_data):
        """Test that watering counts are calculated correctly."""
        result = calculate_daily_summary(sample_raw_data)

        # All times_watered should be >= 1
        assert (result['times_watered'] >= 1).all()

        # Check it's an integer type
        assert result['times_watered'].dtype == 'int64' or result['times_watered'].dtype == 'Int64'

    def test_empty_dataframe(self, empty_dataframe):
        """Test handling of empty DataFrame."""
        result = calculate_daily_summary(empty_dataframe)

        # Should return empty DataFrame with correct columns
        assert result.empty
        assert 'min_temperature' in result.columns
        assert 'avg_temperature' in result.columns

    def test_single_reading_per_plant(self, single_reading_data):
        """Test with exactly one reading per plant per day."""
        result = calculate_daily_summary(single_reading_data)

        # Should have 2 rows (one per plant)
        assert len(result) == 2

        # For single reading, min/max/avg/median should all be equal
        for idx, row in result.iterrows():
            assert row['min_temperature'] == row['max_temperature']
            assert row['min_temperature'] == row['avg_temperature']
            assert row['min_temperature'] == row['median_temperature']

    def test_sorting_by_date_desc(self, sample_raw_data):
        """Test that results are sorted by date descending."""
        result = calculate_daily_summary(sample_raw_data)

        if len(result) > 1:
            dates = result['reading_date'].tolist()
            # Check dates are in descending order
            for i in range(len(dates) - 1):
                assert dates[i] >= dates[i + 1], "Dates should be sorted descending"

    def test_grouping_by_plant_and_date(self, sample_raw_data):
        """Test that data is properly grouped by plant_id and date."""
        result = calculate_daily_summary(sample_raw_data)

        # Each combination of plant_id and reading_date should appear only once
        grouped = result.groupby(['plant_id', 'reading_date']).size()
        assert (grouped == 1).all(), "Each plant/date combination should appear once"

    def test_extreme_values(self, extreme_values_data):
        """Test handling of extreme temperature and humidity values."""
        result = calculate_daily_summary(extreme_values_data)

        assert len(result) == 1
        row = result.iloc[0]

        # Check temperature stats
        assert row['min_temperature'] == 10.0
        assert row['max_temperature'] == 40.0
        assert 10.0 <= row['avg_temperature'] <= 40.0
        assert row['median_temperature'] == 20.0  # Median of [10, 15, 25, 40]
        assert row['percentile_25_temperature'] == 13.75
        assert row['percentile_75_temperature'] == 28.75

        # Check humidity stats
        assert row['min_humidity'] == 0.0
        assert row['max_humidity'] == 100.0

    def test_preserves_botanist_info(self, sample_raw_data):
        """Test that botanist information is preserved correctly."""
        result = calculate_daily_summary(sample_raw_data)

        # Check botanist columns exist and aren't null
        assert result['botanist_name'].notna().all()
        assert result['botanist_email'].notna().all()
        assert result['botanist_phone'].notna().all()

        # Check values match input data
        assert 'John Smith' in result['botanist_name'].values

    def test_date_conversion(self, sample_raw_data):
        """Test that dates are properly converted to datetime."""
        result = calculate_daily_summary(sample_raw_data)

        # reading_date should be datetime type
        assert pd.api.types.is_datetime64_any_dtype(result['reading_date'])

    def test_return_type(self, sample_raw_data):
        """Test that function returns a pandas DataFrame."""
        result = calculate_daily_summary(sample_raw_data)

        assert isinstance(result, pd.DataFrame)

    def test_no_null_statistics(self, sample_raw_data):
        """Test that calculated statistics don't contain null values."""
        result = calculate_daily_summary(sample_raw_data)

        stat_columns = [
            'min_temperature', 'max_temperature', 'avg_temperature',
            'median_temperature', 'percentile_25_temperature', 'percentile_75_temperature',
            'min_humidity', 'max_humidity', 'avg_humidity',
            'median_humidity', 'percentile_25_humidity', 'percentile_75_humidity',
            'times_watered'
        ]

        for col in stat_columns:
            assert result[col].notna().all(), f"Column {col} contains null values"
