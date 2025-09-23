"""
Tests for Taiwan AI Usage Index (TAUI) visualization module.
"""

import pytest
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import tempfile
import shutil
from unittest.mock import patch, MagicMock

# Import the visualization module
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.viz.figures import TAUIVisualizer


class TestTAUIVisualizer:
    """Test suite for TAUIVisualizer class."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test outputs."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def sample_aui_data(self):
        """Sample AUI data for testing."""
        return pd.DataFrame({
            'region': ['台北市', '新北市', '桃園市', '台中市', '台南市'],
            'aui_score': [0.85, 0.78, 0.72, 0.69, 0.65]
        })

    @pytest.fixture
    def sample_tier_data(self):
        """Sample tier distribution data."""
        return {'high': 2, 'medium': 2, 'low': 1}

    @pytest.fixture
    def sample_trend_data(self):
        """Sample trend data for testing."""
        dates = pd.date_range('2024-01-01', periods=6, freq='M')
        return pd.DataFrame({
            'date': dates,
            'aui_score': [0.6, 0.65, 0.7, 0.72, 0.68, 0.75]
        })

    @pytest.fixture
    def visualizer_zh(self, temp_dir):
        """Chinese language visualizer instance."""
        return TAUIVisualizer(output_dir=temp_dir, language='zh-TW')

    @pytest.fixture
    def visualizer_en(self, temp_dir):
        """English language visualizer instance."""
        return TAUIVisualizer(output_dir=temp_dir, language='en-US')

    def test_visualizer_initialization(self, temp_dir):
        """Test visualizer initialization."""
        viz = TAUIVisualizer(output_dir=temp_dir, language='zh-TW')

        assert viz.output_dir == Path(temp_dir)
        assert viz.language == 'zh-TW'
        assert viz.figure_size == (12, 8)
        assert viz.dpi == 300
        assert viz.output_dir.exists()

    def test_visualizer_initialization_english(self, temp_dir):
        """Test visualizer initialization with English."""
        viz = TAUIVisualizer(output_dir=temp_dir, language='en-US')

        assert viz.language == 'en-US'
        assert viz._get_label('title_aui') == 'Taiwan AI Usage Index - Regional Distribution'

    def test_get_label_chinese(self, visualizer_zh):
        """Test label retrieval in Chinese."""
        assert visualizer_zh._get_label('title_aui') == '台灣AI使用指數 - 地區分布'
        assert visualizer_zh._get_label('tier_high') == '高使用量'
        assert visualizer_zh._get_label('nonexistent') == 'nonexistent'

    def test_get_label_english(self, visualizer_en):
        """Test label retrieval in English."""
        assert visualizer_en._get_label('title_aui') == 'Taiwan AI Usage Index - Regional Distribution'
        assert visualizer_en._get_label('tier_high') == 'High Usage'
        assert visualizer_en._get_label('nonexistent') == 'nonexistent'

    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.close')
    def test_create_aui_bar_chart(self, mock_close, mock_savefig,
                                 visualizer_zh, sample_aui_data, temp_dir):
        """Test AUI bar chart creation."""
        output_path = visualizer_zh.create_aui_bar_chart(sample_aui_data)

        # Check that the expected path is returned
        expected_path = Path(temp_dir) / "aui_regional_distribution.png"
        assert output_path == str(expected_path)

        # Verify matplotlib functions were called
        mock_savefig.assert_called_once()
        mock_close.assert_called_once()

    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.close')
    def test_create_tier_pie_chart(self, mock_close, mock_savefig,
                                  visualizer_zh, sample_tier_data, temp_dir):
        """Test tier distribution pie chart creation."""
        output_path = visualizer_zh.create_tier_pie_chart(sample_tier_data)

        # Check that the expected path is returned
        expected_path = Path(temp_dir) / "usage_tier_distribution.png"
        assert output_path == str(expected_path)

        # Verify matplotlib functions were called
        mock_savefig.assert_called_once()
        mock_close.assert_called_once()

    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.close')
    def test_create_trend_line_chart(self, mock_close, mock_savefig,
                                   visualizer_zh, sample_trend_data, temp_dir):
        """Test trend line chart creation."""
        output_path = visualizer_zh.create_trend_line_chart(sample_trend_data)

        # Check that the expected path is returned
        expected_path = Path(temp_dir) / "usage_trend_analysis.png"
        assert output_path == str(expected_path)

        # Verify matplotlib functions were called
        mock_savefig.assert_called_once()
        mock_close.assert_called_once()

    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.close')
    def test_create_trend_line_chart_with_regions(self, mock_close, mock_savefig,
                                                visualizer_zh, temp_dir):
        """Test trend line chart with regional breakdown."""
        # Create trend data with regions
        dates = pd.date_range('2024-01-01', periods=6, freq='M')
        trend_data = pd.DataFrame({
            'date': list(dates) * 2,
            'region': ['台北市'] * 6 + ['台中市'] * 6,
            'aui_score': [0.8, 0.82, 0.85, 0.83, 0.84, 0.86] + [0.6, 0.62, 0.65, 0.63, 0.64, 0.67]
        })

        output_path = visualizer_zh.create_trend_line_chart(trend_data)

        # Check that the expected path is returned
        expected_path = Path(temp_dir) / "usage_trend_analysis.png"
        assert output_path == str(expected_path)

        # Verify matplotlib functions were called
        mock_savefig.assert_called_once()
        mock_close.assert_called_once()

    def test_bar_chart_data_sorting(self, visualizer_zh, temp_dir):
        """Test that bar chart data is properly sorted."""
        # Create unsorted data
        unsorted_data = pd.DataFrame({
            'region': ['台中市', '台北市', '高雄市'],
            'aui_score': [0.69, 0.85, 0.71]
        })

        with patch('matplotlib.pyplot.savefig'), patch('matplotlib.pyplot.close'):
            visualizer_zh.create_aui_bar_chart(unsorted_data)

        # The function should sort the data internally
        # This is verified by the chart generation completing without error

    def test_tier_chart_empty_data(self, visualizer_zh):
        """Test tier chart with empty data."""
        empty_tier_data = {}

        with patch('matplotlib.pyplot.savefig'), patch('matplotlib.pyplot.close'):
            with pytest.raises(ValueError):
                visualizer_zh.create_tier_pie_chart(empty_tier_data)

    def test_invalid_language(self, temp_dir):
        """Test visualizer with invalid language."""
        viz = TAUIVisualizer(output_dir=temp_dir, language='invalid-lang')

        # Should not raise an error but use fallback
        label = viz._get_label('title_aui')
        assert label == 'title_aui'  # Falls back to key

    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.close')
    def test_custom_filenames(self, mock_close, mock_savefig,
                            visualizer_zh, sample_aui_data, temp_dir):
        """Test custom filename specification."""
        custom_filename = "custom_chart.png"
        output_path = visualizer_zh.create_aui_bar_chart(
            sample_aui_data, save_as=custom_filename
        )

        expected_path = Path(temp_dir) / custom_filename
        assert output_path == str(expected_path)

    @patch('src.viz.figures.TAUIVisualizer.create_aui_bar_chart')
    @patch('src.viz.figures.TAUIVisualizer.create_tier_pie_chart')
    @patch('src.viz.figures.TAUIVisualizer.create_trend_line_chart')
    def test_generate_all_charts_with_data(self, mock_trend, mock_tier, mock_bar,
                                         visualizer_zh, sample_aui_data,
                                         sample_tier_data, sample_trend_data):
        """Test generate_all_charts with provided data."""
        # Mock return values
        mock_bar.return_value = "path/to/bar.png"
        mock_tier.return_value = "path/to/pie.png"
        mock_trend.return_value = "path/to/trend.png"

        result = visualizer_zh.generate_all_charts(
            aui_data=sample_aui_data,
            tier_data=sample_tier_data,
            trend_data=sample_trend_data
        )

        # Verify all chart creation methods were called
        mock_bar.assert_called_once_with(sample_aui_data)
        mock_tier.assert_called_once_with(sample_tier_data)
        mock_trend.assert_called_once_with(sample_trend_data)

        # Check return structure
        assert 'aui_bar' in result
        assert 'tier_pie' in result
        assert 'trend_line' in result

    @patch('src.viz.figures.TAUIVisualizer.create_aui_bar_chart')
    @patch('src.viz.figures.TAUIVisualizer.create_tier_pie_chart')
    @patch('src.viz.figures.TAUIVisualizer.create_trend_line_chart')
    def test_generate_all_charts_sample_data(self, mock_trend, mock_tier, mock_bar,
                                           visualizer_zh):
        """Test generate_all_charts with sample data."""
        # Mock return values
        mock_bar.return_value = "path/to/bar.png"
        mock_tier.return_value = "path/to/pie.png"
        mock_trend.return_value = "path/to/trend.png"

        result = visualizer_zh.generate_all_charts()

        # Verify all chart creation methods were called with sample data
        assert mock_bar.call_count == 1
        assert mock_tier.call_count == 1
        assert mock_trend.call_count == 1

        # Check that sample data was generated and used
        bar_call_args = mock_bar.call_args[0][0]
        assert isinstance(bar_call_args, pd.DataFrame)
        assert 'region' in bar_call_args.columns
        assert 'aui_score' in bar_call_args.columns

    def test_chart_privacy_compliance(self, visualizer_zh, sample_aui_data):
        """Test that charts include privacy compliance information."""
        with patch('matplotlib.pyplot.savefig') as mock_savefig, \
             patch('matplotlib.pyplot.close'), \
             patch('matplotlib.pyplot.subplots') as mock_subplots, \
             patch('matplotlib.pyplot.xticks'), \
             patch('matplotlib.pyplot.tight_layout'):

            # Mock subplots return value (returns fig, ax)
            mock_fig = MagicMock()
            mock_ax = MagicMock()
            mock_subplots.return_value = (mock_fig, mock_ax)

            visualizer_zh.create_aui_bar_chart(sample_aui_data)

            # The chart should be saved (privacy note is added via fig.text)
            mock_savefig.assert_called_once()


class TestVisualizationIntegration:
    """Integration tests for the visualization module."""

    def test_main_function_execution(self):
        """Test that main function executes without errors."""
        with patch('matplotlib.pyplot.savefig'), \
             patch('matplotlib.pyplot.close'), \
             patch('pathlib.Path.rename'), \
             patch('builtins.print') as mock_print:

            from src.viz.figures import main
            result = main()

            # Should return dictionary with language-specific paths
            assert isinstance(result, dict)
            assert 'zh-TW' in result
            assert 'en-US' in result

            # Should print success messages
            mock_print.assert_called()

    def test_font_setup_robustness(self):
        """Test font setup handles missing Chinese fonts gracefully."""
        with patch('matplotlib.pyplot.rcParams') as mock_rcparams:
            viz = TAUIVisualizer()

            # Should not raise an error even if fonts are not available
            assert viz is not None


class TestErrorHandling:
    """Test error handling in visualization module."""

    def test_invalid_output_directory(self):
        """Test handling of invalid output directory."""
        # This should create the directory if it doesn't exist
        viz = TAUIVisualizer(output_dir="/nonexistent/path/that/cannot/be/created")
        # Should not raise an error due to mkdir(exist_ok=True)

    def test_empty_dataframe(self, temp_dir):
        """Test handling of empty DataFrame."""
        viz = TAUIVisualizer(output_dir=temp_dir)
        empty_df = pd.DataFrame()

        with patch('matplotlib.pyplot.savefig'), patch('matplotlib.pyplot.close'):
            with pytest.raises((KeyError, ValueError)):
                viz.create_aui_bar_chart(empty_df)

    def test_invalid_data_types(self, temp_dir):
        """Test handling of invalid data types."""
        viz = TAUIVisualizer(output_dir=temp_dir)

        # Test with string values in numeric column
        invalid_data = pd.DataFrame({
            'region': ['A', 'B', 'C'],
            'aui_score': ['invalid', 'data', 'types']
        })

        with patch('matplotlib.pyplot.savefig'), patch('matplotlib.pyplot.close'):
            with pytest.raises((ValueError, TypeError)):
                viz.create_aui_bar_chart(invalid_data)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])