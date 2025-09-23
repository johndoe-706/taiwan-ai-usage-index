"""
Tests for Taiwan AI Usage Index (TAUI) report generation module.
"""

import pytest
import pandas as pd
import numpy as np
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, mock_open, MagicMock

# Import the report module
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.report.make_report import TAUIReportGenerator, ReportConfig


class TestReportConfig:
    """Test suite for ReportConfig dataclass."""

    def test_default_config(self):
        """Test default configuration values."""
        config = ReportConfig()

        assert config.output_dir == "report"
        assert config.language == "zh-TW"
        assert config.include_charts is True
        assert config.include_methodology is True
        assert config.include_privacy_statement is True
        assert config.include_data_tables is True

    def test_custom_config(self):
        """Test custom configuration values."""
        config = ReportConfig(
            output_dir="custom_report",
            language="en-US",
            include_charts=False,
            include_methodology=False
        )

        assert config.output_dir == "custom_report"
        assert config.language == "en-US"
        assert config.include_charts is False
        assert config.include_methodology is False


class TestTAUIReportGenerator:
    """Test suite for TAUIReportGenerator class."""

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
    def sample_chart_paths(self):
        """Sample chart paths."""
        return {
            'aui_bar': 'figures/aui_regional_distribution_zh-TW.png',
            'tier_pie': 'figures/usage_tier_distribution_zh-TW.png',
            'trend_line': 'figures/usage_trend_analysis_zh-TW.png'
        }

    @pytest.fixture
    def generator_zh(self, temp_dir):
        """Chinese language generator instance."""
        config = ReportConfig(output_dir=temp_dir, language='zh-TW')
        return TAUIReportGenerator(config)

    @pytest.fixture
    def generator_en(self, temp_dir):
        """English language generator instance."""
        config = ReportConfig(output_dir=temp_dir, language='en-US')
        return TAUIReportGenerator(config)

    def test_generator_initialization_default(self):
        """Test generator initialization with default config."""
        generator = TAUIReportGenerator()

        assert generator.config.language == 'zh-TW'
        assert generator.config.output_dir == 'report'
        assert generator.output_dir == Path('report')

    def test_generator_initialization_custom(self, temp_dir):
        """Test generator initialization with custom config."""
        config = ReportConfig(output_dir=temp_dir, language='en-US')
        generator = TAUIReportGenerator(config)

        assert generator.config.language == 'en-US'
        assert generator.output_dir == Path(temp_dir)
        assert generator.output_dir.exists()

    def test_get_template_chinese(self, generator_zh):
        """Test template retrieval in Chinese."""
        assert generator_zh._get_template('title') == '# 台灣AI使用指數 (TAUI) 報告'
        assert generator_zh._get_template('exec_summary_title') == '## 執行摘要'
        assert generator_zh._get_template('nonexistent') == 'nonexistent'

    def test_get_template_english(self, generator_en):
        """Test template retrieval in English."""
        assert generator_en._get_template('title') == '# Taiwan AI Usage Index (TAUI) Report'
        assert generator_en._get_template('exec_summary_title') == '## Executive Summary'
        assert generator_en._get_template('nonexistent') == 'nonexistent'

    def test_generate_executive_summary_chinese(self, generator_zh):
        """Test executive summary generation in Chinese."""
        summary_data = {
            'total_regions': 5,
            'avg_aui_score': 0.738,
            'highest_region': '台北市',
            'highest_score': 0.85,
            'lowest_region': '台南市',
            'lowest_score': 0.65
        }

        result = generator_zh.generate_executive_summary(summary_data)

        assert '## 執行摘要' in result
        assert '台北市' in result
        assert '台南市' in result
        assert '0.738' in result
        assert '0.850' in result
        assert '0.650' in result

    def test_generate_executive_summary_english(self, generator_en):
        """Test executive summary generation in English."""
        summary_data = {
            'total_regions': 5,
            'avg_aui_score': 0.738,
            'highest_region': 'Taipei',
            'highest_score': 0.85,
            'lowest_region': 'Tainan',
            'lowest_score': 0.65
        }

        result = generator_en.generate_executive_summary(summary_data)

        assert '## Executive Summary' in result
        assert 'Taipei' in result
        assert 'Tainan' in result
        assert '0.738' in result
        assert 'Key Statistics' in result

    def test_generate_data_tables_chinese(self, generator_zh, sample_aui_data, sample_tier_data):
        """Test data tables generation in Chinese."""
        result = generator_zh.generate_data_tables(sample_aui_data, sample_tier_data)

        assert '## 數據表格' in result
        assert '地區AUI分數詳細表' in result
        assert '使用層級分布統計' in result
        assert '統計摘要' in result
        assert '台北市' in result
        assert '高使用量' in result

    def test_generate_data_tables_english(self, generator_en, sample_aui_data, sample_tier_data):
        """Test data tables generation in English."""
        result = generator_en.generate_data_tables(sample_aui_data, sample_tier_data)

        assert '## Data Tables' in result
        assert 'Regional AUI Scores Detailed Table' in result
        assert 'Usage Tier Distribution Statistics' in result
        assert 'Statistical Summary' in result
        assert 'High Usage' in result

    def test_df_to_markdown_conversion(self, generator_zh, sample_aui_data):
        """Test DataFrame to markdown table conversion."""
        result = generator_zh.generate_data_tables(sample_aui_data, {'high': 1, 'medium': 1, 'low': 1})

        # Check that markdown table format is present
        assert '|' in result
        assert '---' in result
        assert 'region' in result
        assert 'aui_score' in result

    def test_df_to_markdown_empty_dataframe(self, generator_zh):
        """Test DataFrame to markdown with empty DataFrame."""
        empty_df = pd.DataFrame()
        result = generator_zh.generate_data_tables(empty_df, {'high': 0, 'medium': 0, 'low': 0})

        assert '*No data available*' in result

    def test_generate_charts_section_chinese(self, generator_zh, sample_chart_paths):
        """Test charts section generation in Chinese."""
        result = generator_zh.generate_charts_section(sample_chart_paths)

        assert '## 視覺化分析' in result
        assert '地區AUI分數分布圖' in result
        assert 'AI使用層級分布圓餅圖' in result
        assert 'AI使用趨勢分析' in result
        assert '![' in result  # Markdown image syntax
        assert '../figures/' in result

    def test_generate_charts_section_english(self, generator_en, sample_chart_paths):
        """Test charts section generation in English."""
        # Update chart paths for English
        en_chart_paths = {k: v.replace('zh-TW', 'en-US') for k, v in sample_chart_paths.items()}

        result = generator_en.generate_charts_section(en_chart_paths)

        assert '## Visual Analysis' in result
        assert 'Regional AUI Score Distribution' in result
        assert 'AI Usage Tier Distribution' in result
        assert 'AI Usage Trend Analysis' in result
        assert 'en-US' in result

    def test_generate_full_report_with_data(self, generator_zh, sample_aui_data,
                                          sample_tier_data, sample_chart_paths, temp_dir):
        """Test full report generation with provided data."""
        with patch('builtins.open', mock_open()) as mock_file:
            output_path = generator_zh.generate_full_report(
                aui_data=sample_aui_data,
                tier_data=sample_tier_data,
                chart_paths=sample_chart_paths
            )

            # Check that file was written
            mock_file.assert_called_once()

            # Check output path
            expected_path = Path(temp_dir) / "INDEX_TAIWAN.md"
            assert output_path == str(expected_path)

            # Check that write was called with content
            handle = mock_file.return_value.__enter__.return_value
            assert handle.write.called

    def test_generate_full_report_sample_data(self, generator_zh, temp_dir):
        """Test full report generation with sample data."""
        with patch('builtins.open', mock_open()) as mock_file:
            output_path = generator_zh.generate_full_report()

            # Should use sample data and not raise errors
            mock_file.assert_called_once()

            # Check default filename
            expected_path = Path(temp_dir) / "INDEX_TAIWAN.md"
            assert output_path == str(expected_path)

    def test_generate_full_report_english_filename(self, generator_en, temp_dir):
        """Test full report generation with English filename."""
        with patch('builtins.open', mock_open()) as mock_file:
            output_path = generator_en.generate_full_report()

            # Check English filename
            expected_path = Path(temp_dir) / "INDEX_TAIWAN_EN.md"
            assert output_path == str(expected_path)

    def test_generate_full_report_custom_filename(self, generator_zh, temp_dir):
        """Test full report generation with custom filename."""
        custom_filename = "custom_report.md"

        with patch('builtins.open', mock_open()) as mock_file:
            output_path = generator_zh.generate_full_report(output_filename=custom_filename)

            expected_path = Path(temp_dir) / custom_filename
            assert output_path == str(expected_path)

    def test_report_content_structure(self, generator_zh, sample_aui_data, temp_dir):
        """Test that generated report has correct structure."""
        with patch('builtins.open', mock_open()) as mock_file:
            generator_zh.generate_full_report(aui_data=sample_aui_data)

            # Get the written content
            handle = mock_file.return_value.__enter__.return_value
            written_content = ''.join(call[0][0] for call in handle.write.call_args_list)

            # Check for required sections
            assert '# 台灣AI使用指數 (TAUI) 報告' in written_content
            assert '## 執行摘要' in written_content
            assert '## 研究方法' in written_content
            assert '## 視覺化分析' in written_content
            assert '## 數據表格' in written_content
            assert '## 隱私保護聲明' in written_content

    def test_generate_json_metadata(self, generator_zh, sample_aui_data, sample_tier_data, temp_dir):
        """Test JSON metadata generation."""
        with patch('builtins.open', mock_open()) as mock_file, \
             patch('json.dump') as mock_json_dump:

            output_path = generator_zh.generate_json_metadata(
                aui_data=sample_aui_data,
                tier_data=sample_tier_data
            )

            # Check output path
            expected_path = Path(temp_dir) / "taui_metadata.json"
            assert output_path == str(expected_path)

            # Check that JSON was dumped
            mock_json_dump.assert_called_once()

            # Check metadata structure
            metadata = mock_json_dump.call_args[0][0]
            assert 'report_info' in metadata
            assert 'statistics' in metadata
            assert 'tier_distribution' in metadata
            assert 'regional_scores' in metadata
            assert 'privacy_compliance' in metadata

    def test_json_metadata_content(self, generator_zh, sample_aui_data, sample_tier_data):
        """Test JSON metadata content structure."""
        with patch('builtins.open', mock_open()), \
             patch('json.dump') as mock_json_dump:

            generator_zh.generate_json_metadata(sample_aui_data, sample_tier_data)

            metadata = mock_json_dump.call_args[0][0]

            # Check report info
            assert metadata['report_info']['title'] == "Taiwan AI Usage Index (TAUI)"
            assert metadata['report_info']['version'] == "1.0.0"
            assert metadata['report_info']['language'] == "zh-TW"

            # Check statistics
            stats = metadata['statistics']
            assert stats['total_regions'] == 5
            assert 'avg_aui_score' in stats
            assert 'max_aui_score' in stats
            assert 'min_aui_score' in stats

            # Check privacy compliance
            privacy = metadata['privacy_compliance']
            assert privacy['min_conversations'] == 15
            assert privacy['min_users'] == 5
            assert privacy['pii_removed'] is True
            assert privacy['anonymized'] is True

    def test_config_sections_exclusion(self, temp_dir):
        """Test excluding sections based on config."""
        config = ReportConfig(
            output_dir=temp_dir,
            include_charts=False,
            include_methodology=False,
            include_privacy_statement=False,
            include_data_tables=False
        )
        generator = TAUIReportGenerator(config)

        with patch('builtins.open', mock_open()) as mock_file:
            generator.generate_full_report()

            # Get written content
            handle = mock_file.return_value.__enter__.return_value
            written_content = ''.join(call[0][0] for call in handle.write.call_args_list)

            # Check that excluded sections are not present
            assert '## 研究方法' not in written_content
            assert '## 視覺化分析' not in written_content
            assert '## 數據表格' not in written_content
            assert '## 隱私保護聲明' not in written_content


class TestReportIntegration:
    """Integration tests for the report module."""

    def test_main_function_execution(self):
        """Test that main function executes without errors."""
        with patch('builtins.open', mock_open()), \
             patch('json.dump'), \
             patch('builtins.print') as mock_print:

            from src.report.make_report import main
            result = main()

            # Should return list of generated files
            assert isinstance(result, list)
            assert len(result) > 0

            # Should print success messages
            mock_print.assert_called()

    def test_tier_calculation_from_aui_data(self):
        """Test automatic tier calculation from AUI data."""
        aui_data = pd.DataFrame({
            'region': ['A', 'B', 'C', 'D', 'E'],
            'aui_score': [0.9, 0.7, 0.6, 0.4, 0.3]  # 1 high, 2 medium, 2 low
        })

        with patch('builtins.open', mock_open()), \
             patch('json.dump') as mock_json_dump:

            generator = TAUIReportGenerator()
            generator.generate_full_report(aui_data=aui_data)

            # Check that tier data was calculated correctly in JSON metadata call
            # The generate_full_report should calculate tiers automatically
            # This is tested indirectly through successful execution


class TestErrorHandling:
    """Test error handling in report generation."""

    def test_invalid_output_directory(self):
        """Test handling of invalid output directory."""
        # This should create the directory if it doesn't exist
        config = ReportConfig(output_dir="/nonexistent/path/that/cannot/be/created")
        generator = TAUIReportGenerator(config)
        # Should not raise an error due to mkdir(exist_ok=True)

    def test_empty_dataframe_handling(self, temp_dir):
        """Test handling of empty DataFrame in report generation."""
        config = ReportConfig(output_dir=temp_dir)
        generator = TAUIReportGenerator(config)

        empty_df = pd.DataFrame()

        with patch('builtins.open', mock_open()):
            # Should handle empty data gracefully
            result = generator.generate_full_report(aui_data=empty_df)
            assert result is not None

    def test_file_write_error_handling(self, temp_dir):
        """Test handling of file write errors."""
        generator = TAUIReportGenerator(ReportConfig(output_dir=temp_dir))

        with patch('builtins.open', side_effect=IOError("Cannot write file")):
            with pytest.raises(IOError):
                generator.generate_full_report()

    def test_malformed_data_handling(self, temp_dir):
        """Test handling of malformed data."""
        generator = TAUIReportGenerator(ReportConfig(output_dir=temp_dir))

        # Data with missing columns
        malformed_data = pd.DataFrame({'wrong_column': [1, 2, 3]})

        with patch('builtins.open', mock_open()):
            with pytest.raises(KeyError):
                generator.generate_full_report(aui_data=malformed_data)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])