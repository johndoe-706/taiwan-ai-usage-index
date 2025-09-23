"""
Test suite for TAUI ingest module.
Tests data ingestion, filtering, and conversion functionality.
"""

import pytest
import pandas as pd
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
import os

from src.ingest.anthropic_open_data import (
    read_anthropic_csv,
    filter_taiwan_and_peers,
    convert_to_parquet,
    process_anthropic_data,
    PEER_COUNTRIES
)


class TestAnthropicOpenData:
    """Test class for Anthropic open data ingestion."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def sample_csv_data(self):
        """Sample CSV data for testing."""
        return pd.DataFrame({
            'country_code': ['TWN', 'USA', 'SGP', 'KOR', 'JPN', 'HKG', 'GBR'],
            'conversation_count': [100, 1000, 80, 120, 150, 90, 200],
            'user_count': [50, 500, 40, 60, 75, 45, 100],
            'timestamp': ['2024-01-01', '2024-01-01', '2024-01-01',
                         '2024-01-01', '2024-01-01', '2024-01-01', '2024-01-01'],
            'unknown_column': ['a', 'b', 'c', 'd', 'e', 'f', 'g']
        })

    @pytest.fixture
    def sample_csv_file(self, temp_dir, sample_csv_data):
        """Create sample CSV file for testing."""
        csv_path = temp_dir / "test_data.csv"
        sample_csv_data.to_csv(csv_path, index=False)
        return csv_path

    def test_peer_countries_constant(self):
        """Test that PEER_COUNTRIES includes expected countries."""
        expected_countries = {'TWN', 'SGP', 'KOR', 'JPN', 'HKG'}
        assert PEER_COUNTRIES == expected_countries

    def test_read_anthropic_csv_success(self, sample_csv_file):
        """Test successful CSV reading."""
        df = read_anthropic_csv(sample_csv_file)
        assert not df.empty
        assert len(df) == 7
        assert 'country_code' in df.columns
        assert 'conversation_count' in df.columns

    def test_read_anthropic_csv_file_not_found(self, temp_dir):
        """Test CSV reading with non-existent file."""
        non_existent_file = temp_dir / "non_existent.csv"
        with pytest.raises(FileNotFoundError):
            read_anthropic_csv(non_existent_file)

    def test_read_anthropic_csv_invalid_format(self, temp_dir):
        """Test CSV reading with invalid file format."""
        invalid_file = temp_dir / "invalid.csv"
        with open(invalid_file, 'w') as f:
            f.write("invalid,csv,format\nwith,missing,quotes")

        # Should handle gracefully or raise appropriate error
        with pytest.raises((pd.errors.ParserError, ValueError)):
            read_anthropic_csv(invalid_file)

    def test_filter_taiwan_and_peers(self, sample_csv_data):
        """Test filtering for Taiwan and peer countries."""
        filtered_df = filter_taiwan_and_peers(sample_csv_data)

        # Should include TWN, SGP, KOR, JPN, HKG (5 countries)
        assert len(filtered_df) == 5
        assert set(filtered_df['country_code'].unique()) == PEER_COUNTRIES

        # Should exclude USA, GBR
        assert 'USA' not in filtered_df['country_code'].values
        assert 'GBR' not in filtered_df['country_code'].values

    def test_filter_taiwan_and_peers_empty_input(self):
        """Test filtering with empty DataFrame."""
        empty_df = pd.DataFrame()
        filtered_df = filter_taiwan_and_peers(empty_df)
        assert filtered_df.empty

    def test_filter_taiwan_and_peers_no_country_column(self):
        """Test filtering when country_code column is missing."""
        df_no_country = pd.DataFrame({
            'conversation_count': [100, 200],
            'user_count': [50, 100]
        })

        with pytest.raises(KeyError):
            filter_taiwan_and_peers(df_no_country)

    def test_filter_taiwan_and_peers_no_matches(self):
        """Test filtering when no peer countries are present."""
        df_no_peers = pd.DataFrame({
            'country_code': ['USA', 'GBR', 'FRA'],
            'conversation_count': [100, 200, 300],
            'user_count': [50, 100, 150]
        })

        filtered_df = filter_taiwan_and_peers(df_no_peers)
        assert filtered_df.empty

    def test_convert_to_parquet_success(self, temp_dir, sample_csv_data):
        """Test successful parquet conversion."""
        output_path = temp_dir / "output.parquet"
        convert_to_parquet(sample_csv_data, output_path)

        assert output_path.exists()

        # Read back and verify
        df_read = pd.read_parquet(output_path)
        pd.testing.assert_frame_equal(sample_csv_data, df_read)

    def test_convert_to_parquet_creates_directory(self, temp_dir, sample_csv_data):
        """Test that parquet conversion creates output directory."""
        nested_path = temp_dir / "nested" / "dir" / "output.parquet"
        convert_to_parquet(sample_csv_data, nested_path)

        assert nested_path.exists()
        assert nested_path.parent.exists()

    def test_convert_to_parquet_empty_dataframe(self, temp_dir):
        """Test parquet conversion with empty DataFrame."""
        empty_df = pd.DataFrame()
        output_path = temp_dir / "empty.parquet"

        convert_to_parquet(empty_df, output_path)
        assert output_path.exists()

        df_read = pd.read_parquet(output_path)
        assert df_read.empty

    @patch('src.ingest.anthropic_open_data.read_anthropic_csv')
    @patch('src.ingest.anthropic_open_data.filter_taiwan_and_peers')
    @patch('src.ingest.anthropic_open_data.convert_to_parquet')
    def test_process_anthropic_data_integration(self, mock_convert, mock_filter, mock_read, temp_dir):
        """Test the main processing function integration."""
        # Setup mocks
        mock_df = pd.DataFrame({'country_code': ['TWN'], 'count': [100]})
        mock_read.return_value = mock_df
        mock_filter.return_value = mock_df

        input_path = temp_dir / "input.csv"
        output_path = temp_dir / "output.parquet"

        # Execute
        result = process_anthropic_data(input_path, output_path)

        # Verify calls
        mock_read.assert_called_once_with(input_path)
        mock_filter.assert_called_once_with(mock_df)
        mock_convert.assert_called_once_with(mock_df, output_path)

        # Verify return value
        pd.testing.assert_frame_equal(result, mock_df)

    def test_process_anthropic_data_end_to_end(self, temp_dir, sample_csv_data):
        """Test complete end-to-end processing."""
        # Create input CSV
        input_path = temp_dir / "input.csv"
        sample_csv_data.to_csv(input_path, index=False)

        # Define output path
        output_path = temp_dir / "output.parquet"

        # Process data
        result_df = process_anthropic_data(input_path, output_path)

        # Verify output file exists
        assert output_path.exists()

        # Verify result contains only peer countries
        assert len(result_df) == 5
        assert set(result_df['country_code'].unique()) == PEER_COUNTRIES

        # Verify parquet file content
        df_from_file = pd.read_parquet(output_path)
        pd.testing.assert_frame_equal(result_df, df_from_file)

    def test_process_anthropic_data_handles_unknown_columns(self, temp_dir):
        """Test that processing handles unknown columns gracefully."""
        # Create CSV with unknown columns
        data_with_unknowns = pd.DataFrame({
            'country_code': ['TWN', 'SGP'],
            'conversation_count': [100, 80],
            'unknown_col1': ['x', 'y'],
            'weird_column': [1.5, 2.7],
            'future_column': [None, None]
        })

        input_path = temp_dir / "with_unknowns.csv"
        data_with_unknowns.to_csv(input_path, index=False)

        output_path = temp_dir / "output_unknowns.parquet"

        # Should process without errors
        result_df = process_anthropic_data(input_path, output_path)

        # Verify all columns are preserved
        assert 'unknown_col1' in result_df.columns
        assert 'weird_column' in result_df.columns
        assert 'future_column' in result_df.columns

        assert len(result_df) == 2  # TWN and SGP

    def test_process_anthropic_data_file_permissions(self, temp_dir, sample_csv_data):
        """Test handling of file permission issues."""
        input_path = temp_dir / "input.csv"
        sample_csv_data.to_csv(input_path, index=False)

        # Try to write to a read-only location (simulate permission error)
        if os.name == 'nt':  # Windows
            readonly_dir = Path("C:\\Windows\\System32")
        else:  # Unix-like
            readonly_dir = Path("/root")

        output_path = readonly_dir / "output.parquet"

        # Should raise PermissionError or similar
        with pytest.raises((PermissionError, OSError)):
            process_anthropic_data(input_path, output_path)

    @pytest.mark.parametrize("country_codes,expected_count", [
        (['TWN'], 1),
        (['TWN', 'SGP'], 2),
        (['TWN', 'SGP', 'KOR', 'JPN', 'HKG'], 5),
        (['TWN', 'USA', 'SGP'], 2),  # USA should be filtered out
        (['USA', 'GBR'], 0),  # No peer countries
    ])
    def test_filter_parametrized(self, country_codes, expected_count):
        """Parametrized test for different country code combinations."""
        df = pd.DataFrame({
            'country_code': country_codes,
            'conversation_count': [100] * len(country_codes)
        })

        filtered_df = filter_taiwan_and_peers(df)
        assert len(filtered_df) == expected_count

    def test_large_dataset_performance(self, temp_dir):
        """Test performance with larger dataset."""
        # Create large dataset
        large_data = pd.DataFrame({
            'country_code': ['TWN'] * 10000 + ['USA'] * 5000 + ['SGP'] * 3000,
            'conversation_count': range(18000),
            'user_count': range(18000),
            'timestamp': ['2024-01-01'] * 18000
        })

        input_path = temp_dir / "large_input.csv"
        large_data.to_csv(input_path, index=False)

        output_path = temp_dir / "large_output.parquet"

        # Should complete without timeout
        result_df = process_anthropic_data(input_path, output_path)

        # Verify only peer countries remain
        assert len(result_df) == 13000  # TWN + SGP
        assert set(result_df['country_code'].unique()) == {'TWN', 'SGP'}

    def test_data_types_preservation(self, temp_dir):
        """Test that data types are preserved through processing."""
        typed_data = pd.DataFrame({
            'country_code': ['TWN', 'SGP'],
            'conversation_count': [100, 80],
            'user_count': [50, 40],
            'float_col': [1.5, 2.7],
            'timestamp': pd.to_datetime(['2024-01-01', '2024-01-02']),
            'bool_col': [True, False]
        })

        input_path = temp_dir / "typed_input.csv"
        typed_data.to_csv(input_path, index=False)

        output_path = temp_dir / "typed_output.parquet"

        result_df = process_anthropic_data(input_path, output_path)

        # Read back from parquet
        df_from_file = pd.read_parquet(output_path)

        # Verify data types are reasonable (some conversion expected with CSV roundtrip)
        assert df_from_file['conversation_count'].dtype in ['int64', 'int32']
        assert df_from_file['user_count'].dtype in ['int64', 'int32']
        assert 'float' in str(df_from_file['float_col'].dtype)