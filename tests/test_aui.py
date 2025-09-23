"""
Comprehensive tests for AUI (AI Usage Index) calculation module.

Tests follow TDD principles with coverage for:
- AUI calculation (usage% / working-age population%)
- Privacy filters (min_conv=15, min_users=5)
- Tiering system implementation
- Demo mode functionality
- CSV output validation
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, mock_open
import tempfile
import os
from pathlib import Path

# Import the module under test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.metrics.aui import (
    AUICalculator,
    apply_privacy_filters,
    calculate_aui_score,
    assign_usage_tier,
    generate_demo_data,
    main,
    compute_country_aui,
    assign_tier,
    TierThresholds
)


class TestPrivacyFilters:
    """Test privacy filtering functionality."""

    def test_apply_privacy_filters_removes_low_conversation_counts(self):
        """Test that entries with <15 conversations are removed."""
        data = pd.DataFrame({
            'region': ['台北市', '台中市', '高雄市'],
            'conversation_count': [10, 20, 5],
            'unique_users': [8, 15, 3]
        })

        filtered = apply_privacy_filters(data, min_conv=15, min_users=5)

        assert len(filtered) == 1
        assert filtered.iloc[0]['region'] == '台中市'

    def test_apply_privacy_filters_removes_low_user_counts(self):
        """Test that entries with <5 users are removed."""
        data = pd.DataFrame({
            'region': ['台北市', '台中市', '高雄市'],
            'conversation_count': [20, 25, 30],
            'unique_users': [3, 8, 12]
        })

        filtered = apply_privacy_filters(data, min_conv=15, min_users=5)

        assert len(filtered) == 2
        assert '台北市' not in filtered['region'].values

    def test_apply_privacy_filters_keeps_valid_entries(self):
        """Test that entries meeting both criteria are kept."""
        data = pd.DataFrame({
            'region': ['台北市', '台中市'],
            'conversation_count': [100, 200],
            'unique_users': [50, 75]
        })

        filtered = apply_privacy_filters(data, min_conv=15, min_users=5)

        assert len(filtered) == 2
        assert all(filtered['conversation_count'] >= 15)
        assert all(filtered['unique_users'] >= 5)

    def test_apply_privacy_filters_custom_thresholds(self):
        """Test privacy filters with custom thresholds."""
        data = pd.DataFrame({
            'region': ['A', 'B', 'C'],
            'conversation_count': [5, 10, 20],
            'unique_users': [2, 5, 10]
        })

        filtered = apply_privacy_filters(data, min_conv=10, min_users=5)

        assert len(filtered) == 2
        assert 'A' not in filtered['region'].values

    def test_privacy_filters_legacy_compatibility(self):
        """Test compatibility with original column names."""
        df = pd.DataFrame({
            'geo':['X','Y','Z'],
            'conversations':[14, 15, 100],
            'unique_users':[10, 4, 50]
        })
        out = apply_privacy_filters(df, min_conv=15, min_users=5)
        # 'X': conv<15 -> drop; 'Y': users<5 -> drop; 'Z': keep
        assert list(out['geo']) == ['Z']


class TestAUICalculation:
    """Test AUI score calculation functionality."""

    def test_calculate_aui_score_basic(self):
        """Test basic AUI calculation formula."""
        # AUI = (usage_percentage / working_age_percentage) * 100
        usage_pct = 25.0  # 25% usage
        working_age_pct = 50.0  # 50% working age population

        aui = calculate_aui_score(usage_pct, working_age_pct)

        expected = (25.0 / 50.0) * 100
        assert aui == expected
        assert aui == 50.0

    def test_calculate_aui_score_edge_cases(self):
        """Test AUI calculation edge cases."""
        # Test zero working age population
        with pytest.raises(ValueError, match="Working age percentage cannot be zero"):
            calculate_aui_score(25.0, 0.0)

        # Test negative values
        with pytest.raises(ValueError, match="Percentages must be non-negative"):
            calculate_aui_score(-5.0, 50.0)

        with pytest.raises(ValueError, match="Percentages must be non-negative"):
            calculate_aui_score(25.0, -10.0)

    def test_calculate_aui_score_high_usage(self):
        """Test AUI with high usage relative to working age population."""
        aui = calculate_aui_score(80.0, 60.0)
        expected = (80.0 / 60.0) * 100
        assert abs(aui - expected) < 0.001
        assert aui > 100  # High usage index


class TestUsageTiers:
    """Test usage tier assignment functionality."""

    def test_assign_usage_tier_low(self):
        """Test assignment to low tier."""
        assert assign_usage_tier(25.0) == "低度使用"
        assert assign_usage_tier(49.9) == "低度使用"

    def test_assign_usage_tier_medium(self):
        """Test assignment to medium tier."""
        assert assign_usage_tier(50.0) == "中度使用"
        assert assign_usage_tier(75.0) == "中度使用"
        assert assign_usage_tier(99.9) == "中度使用"

    def test_assign_usage_tier_high(self):
        """Test assignment to high tier."""
        assert assign_usage_tier(100.0) == "高度使用"
        assert assign_usage_tier(150.0) == "高度使用"
        assert assign_usage_tier(200.0) == "高度使用"

    def test_assign_usage_tier_edge_cases(self):
        """Test tier assignment edge cases."""
        assert assign_usage_tier(0.0) == "低度使用"
        assert assign_usage_tier(49.99999) == "低度使用"
        assert assign_usage_tier(50.00001) == "中度使用"
        assert assign_usage_tier(99.99999) == "中度使用"
        assert assign_usage_tier(100.00001) == "高度使用"


class TestLegacyCompatibility:
    """Test backward compatibility with original implementation."""

    def test_aui_basic_ratio(self):
        """Test original AUI ratio calculation."""
        usage = pd.DataFrame({'country_code':['A','B'], 'conversations':[50,50]})
        pop = pd.DataFrame({'country_code':['A','B'], 'working_age_pop':[1,9]})
        out = compute_country_aui(usage, pop).set_index('country_code')
        # Usage shares are 0.5/0.5, pop shares are 0.1/0.9 -> AUI are 5.0 and 0.555...
        assert abs(out.loc['A','AUI'] - 5.0) < 1e-6
        assert abs(out.loc['B','AUI'] - (0.5/0.9)) < 1e-6

    def test_tiers_ordering(self):
        """Test original tier assignment."""
        th = TierThresholds(minimal=0.5, emerging=0.9, lower=1.1, upper=1.84, leading=7.0)
        assert assign_tier(0.3, th) == 'below-min'
        assert assign_tier(0.7, th) == 'emerging'
        assert assign_tier(1.05, th) == 'lower'
        assert assign_tier(1.7, th) == 'upper'
        assert assign_tier(2.0, th) == 'leading'


class TestAUICalculator:
    """Test the main AUICalculator class."""

    def test_aui_calculator_init(self):
        """Test AUICalculator initialization."""
        calc = AUICalculator()
        assert calc.min_conversations == 15
        assert calc.min_users == 5

        calc_custom = AUICalculator(min_conversations=20, min_users=10)
        assert calc_custom.min_conversations == 20
        assert calc_custom.min_users == 10

    def test_aui_calculator_process_data(self):
        """Test full data processing pipeline."""
        calc = AUICalculator()

        # Create test data
        data = pd.DataFrame({
            'region': ['台北市', '台中市', '高雄市', '台南市'],
            'conversation_count': [100, 50, 20, 5],  # Last one below threshold
            'unique_users': [25, 15, 8, 2],  # Last one below threshold
            'total_population': [2000, 1500, 1200, 800],
            'working_age_population': [1200, 900, 720, 480]
        })

        result = calc.process_data(data)

        # Should filter out the last entry (台南市)
        assert len(result) == 3
        assert '台南市' not in result['region'].values

        # Check calculated columns exist
        required_columns = [
            'region', 'conversation_count', 'unique_users',
            'total_population', 'working_age_population',
            'usage_percentage', 'working_age_percentage',
            'aui_score', 'usage_tier'
        ]
        for col in required_columns:
            assert col in result.columns

    def test_aui_calculator_save_results(self):
        """Test saving results to CSV."""
        calc = AUICalculator()

        # Create test result data
        result_data = pd.DataFrame({
            'region': ['台北市', '台中市'],
            'aui_score': [75.5, 125.3],
            'usage_tier': ['中度使用', '高度使用']
        })

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, 'test_output.csv')
            calc.save_results(result_data, output_path)

            # Verify file was created and contains correct data
            assert os.path.exists(output_path)

            loaded_data = pd.read_csv(output_path, encoding='utf-8-sig')
            assert len(loaded_data) == 2
            assert list(loaded_data['region']) == ['台北市', '台中市']


class TestDemoMode:
    """Test demo mode functionality."""

    def test_generate_demo_data(self):
        """Test demo data generation."""
        demo_data = generate_demo_data()

        assert isinstance(demo_data, pd.DataFrame)
        assert len(demo_data) >= 5  # Should have multiple regions

        # Check required columns
        required_columns = [
            'region', 'conversation_count', 'unique_users',
            'total_population', 'working_age_population'
        ]
        for col in required_columns:
            assert col in demo_data.columns

        # Check data ranges make sense
        assert all(demo_data['conversation_count'] > 0)
        assert all(demo_data['unique_users'] > 0)
        assert all(demo_data['total_population'] > demo_data['working_age_population'])
        assert all(demo_data['working_age_population'] > 0)

    def test_demo_data_privacy_compliance(self):
        """Test that demo data meets privacy requirements by default."""
        demo_data = generate_demo_data()

        # All entries should meet privacy thresholds
        assert all(demo_data['conversation_count'] >= 15)
        assert all(demo_data['unique_users'] >= 5)


class TestMainFunction:
    """Test the main function and CLI interface."""

    @patch('sys.argv', ['aui.py', '--demo'])
    @patch('src.metrics.aui.generate_demo_data')
    def test_main_demo_mode(self, mock_demo_data):
        """Test main function in demo mode."""
        # Setup mock demo data
        mock_data = pd.DataFrame({
            'region': ['台北市'],
            'conversation_count': [100],
            'unique_users': [25],
            'total_population': [2000],
            'working_age_population': [1200]
        })
        mock_demo_data.return_value = mock_data

        with patch('src.metrics.aui.AUICalculator.save_results') as mock_save:
            with patch('builtins.print') as mock_print:
                main()

                # Verify demo mode was activated
                mock_demo_data.assert_called_once()
                mock_save.assert_called_once()

                # Check that results were printed
                assert mock_print.called


class TestIntegration:
    """Integration tests for the complete workflow."""

    def test_full_pipeline_integration(self):
        """Test complete pipeline from data to results."""
        # Create realistic test data
        raw_data = pd.DataFrame({
            'region': ['台北市', '新北市', '台中市', '台南市', '高雄市', '桃園市'],
            'conversation_count': [1000, 800, 600, 400, 500, 300],
            'unique_users': [200, 160, 120, 80, 100, 60],
            'total_population': [2500000, 4000000, 2800000, 1880000, 2770000, 2250000],
            'working_age_population': [1750000, 2800000, 1960000, 1316000, 1939000, 1575000]
        })

        calc = AUICalculator(min_conversations=350, min_users=70)
        result = calc.process_data(raw_data)

        # Should filter out regions not meeting privacy thresholds
        assert len(result) < len(raw_data)

        # Verify calculations
        for _, row in result.iterrows():
            expected_usage_pct = (row['unique_users'] / row['total_population']) * 100
            expected_working_age_pct = (row['working_age_population'] / row['total_population']) * 100
            expected_aui = (expected_usage_pct / expected_working_age_pct) * 100

            assert abs(row['usage_percentage'] - expected_usage_pct) < 0.001
            assert abs(row['working_age_percentage'] - expected_working_age_pct) < 0.001
            assert abs(row['aui_score'] - expected_aui) < 0.001

            # Verify tier assignment
            if row['aui_score'] < 50:
                assert row['usage_tier'] == "低度使用"
            elif row['aui_score'] < 100:
                assert row['usage_tier'] == "中度使用"
            else:
                assert row['usage_tier'] == "高度使用"

    def test_empty_data_handling(self):
        """Test handling of empty datasets."""
        calc = AUICalculator()
        empty_data = pd.DataFrame()

        result = calc.process_data(empty_data)
        assert len(result) == 0
        assert isinstance(result, pd.DataFrame)

    def test_all_filtered_data_handling(self):
        """Test handling when all data is filtered out."""
        calc = AUICalculator()

        # Data that doesn't meet privacy thresholds
        low_usage_data = pd.DataFrame({
            'region': ['A', 'B'],
            'conversation_count': [5, 10],
            'unique_users': [2, 3],
            'total_population': [1000, 2000],
            'working_age_population': [600, 1200]
        })

        result = calc.process_data(low_usage_data)
        assert len(result) == 0
        assert isinstance(result, pd.DataFrame)
