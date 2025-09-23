"""
Taiwan AI Usage Index (TAUI) - P3 Metrics Module

Implements AUI calculation for Taiwan regional analysis with:
- Regional usage percentage vs working-age population percentage
- Privacy filters (min_conv=15, min_users=5)
- Chinese tier system (低度使用/中度使用/高度使用)
- Demo mode with realistic Taiwan data
- CSV output functionality
"""

import pandas as pd
import numpy as np
import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any


@dataclass
class TierThresholds:
    """Configurable thresholds for AUI tier assignment."""
    # Default bins are configurable; tune to match report bins.
    minimal: float = 0.50
    emerging: float = 0.90
    lower: float = 1.10
    upper: float = 1.84
    leading: float = 7.00


class AUICalculator:
    """
    Taiwan AI Usage Index Calculator.

    Calculates AUI scores for Taiwan regions with privacy filtering
    and tier assignment in Chinese.
    """

    def __init__(self, min_conversations: int = 15, min_users: int = 5):
        """
        Initialize AUI calculator.

        Args:
            min_conversations: Minimum conversations for privacy filter
            min_users: Minimum users for privacy filter
        """
        self.min_conversations = min_conversations
        self.min_users = min_users

    def process_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Process raw data through complete AUI pipeline.

        Args:
            data: DataFrame with columns ['region', 'conversation_count',
                  'unique_users', 'total_population', 'working_age_population']

        Returns:
            Processed DataFrame with AUI scores and tiers
        """
        if data.empty:
            return pd.DataFrame()

        # Apply privacy filters
        filtered_data = apply_privacy_filters(
            data,
            min_conv=self.min_conversations,
            min_users=self.min_users
        )

        if filtered_data.empty:
            return pd.DataFrame()

        # Calculate percentages and AUI scores
        result = filtered_data.copy()
        result['usage_percentage'] = (result['unique_users'] / result['total_population']) * 100
        result['working_age_percentage'] = (result['working_age_population'] / result['total_population']) * 100

        # Calculate AUI scores
        result['aui_score'] = result.apply(
            lambda row: calculate_aui_score(row['usage_percentage'], row['working_age_percentage']),
            axis=1
        )

        # Assign usage tiers in Chinese
        result['usage_tier'] = result['aui_score'].apply(assign_usage_tier)

        return result

    def save_results(self, data: pd.DataFrame, output_path: str) -> None:
        """
        Save results to CSV file.

        Args:
            data: Processed DataFrame with results
            output_path: Path to save CSV file
        """
        # Ensure output directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # Save to CSV with UTF-8 encoding for Chinese characters
        data.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"結果已保存至: {output_path}")


def calculate_aui_score(usage_percentage: float, working_age_percentage: float) -> float:
    """
    Calculate AUI score using the formula: (usage% / working_age%) * 100

    Args:
        usage_percentage: Percentage of users in total population
        working_age_percentage: Percentage of working age population

    Returns:
        AUI score

    Raises:
        ValueError: If percentages are invalid
    """
    if usage_percentage < 0 or working_age_percentage < 0:
        raise ValueError("Percentages must be non-negative")

    if working_age_percentage == 0:
        raise ValueError("Working age percentage cannot be zero")

    return (usage_percentage / working_age_percentage) * 100


def assign_usage_tier(aui_score: float) -> str:
    """
    Assign usage tier in Chinese based on AUI score.

    Args:
        aui_score: Calculated AUI score

    Returns:
        Usage tier in Chinese:
        - "低度使用" (Low usage): AUI < 50
        - "中度使用" (Medium usage): 50 <= AUI < 100
        - "高度使用" (High usage): AUI >= 100
    """
    if aui_score < 50:
        return "低度使用"
    elif aui_score < 100:
        return "中度使用"
    else:
        return "高度使用"


def generate_demo_data() -> pd.DataFrame:
    """
    Generate realistic demo data for Taiwan regions.

    Returns:
        DataFrame with demo data for Taiwan cities/counties
    """
    demo_regions = [
        {"region": "台北市", "conversation_count": 1200, "unique_users": 240,
         "total_population": 2500000, "working_age_population": 1750000},
        {"region": "新北市", "conversation_count": 1800, "unique_users": 360,
         "total_population": 4000000, "working_age_population": 2800000},
        {"region": "桃園市", "conversation_count": 900, "unique_users": 180,
         "total_population": 2250000, "working_age_population": 1575000},
        {"region": "台中市", "conversation_count": 1100, "unique_users": 220,
         "total_population": 2800000, "working_age_population": 1960000},
        {"region": "台南市", "conversation_count": 750, "unique_users": 150,
         "total_population": 1880000, "working_age_population": 1316000},
        {"region": "高雄市", "conversation_count": 1000, "unique_users": 200,
         "total_population": 2770000, "working_age_population": 1939000},
        {"region": "基隆市", "conversation_count": 150, "unique_users": 30,
         "total_population": 370000, "working_age_population": 259000},
        {"region": "新竹市", "conversation_count": 200, "unique_users": 40,
         "total_population": 450000, "working_age_population": 315000},
        {"region": "嘉義市", "conversation_count": 120, "unique_users": 24,
         "total_population": 270000, "working_age_population": 189000},
        {"region": "新竹縣", "conversation_count": 280, "unique_users": 56,
         "total_population": 570000, "working_age_population": 399000},
    ]

    return pd.DataFrame(demo_regions)

def compute_share(series: pd.Series) -> pd.Series:
    total = series.sum()
    if total == 0:
        return series.copy() * np.nan
    return series / total

def compute_country_aui(df_usage: pd.DataFrame, df_pop: pd.DataFrame) -> pd.DataFrame:
    """Compute AUI by country: usage_share / pop_share (15–64).
    df_usage: columns ['country_code','conversations']
    df_pop:   columns ['country_code','working_age_pop']
    """
    u = df_usage.groupby('country_code', as_index=False)['conversations'].sum()
    u['usage_share'] = compute_share(u['conversations'])
    p = df_pop.groupby('country_code', as_index=False)['working_age_pop'].sum()
    p['pop_share'] = compute_share(p['working_age_pop'])
    m = pd.merge(u, p, on='country_code', how='inner')
    m['AUI'] = m['usage_share'] / m['pop_share']
    return m

def apply_privacy_filters(df: pd.DataFrame, min_conv: int = 15, min_users: int = 5) -> pd.DataFrame:
    """
    Apply privacy filters to remove entries with insufficient data.

    Args:
        df: DataFrame with conversation and user data
        min_conv: Minimum conversations threshold
        min_users: Minimum users threshold

    Returns:
        Filtered DataFrame meeting privacy requirements
    """
    if df.empty:
        return df.copy()

    cols = df.columns
    ok = pd.Series(True, index=df.index)

    # Check for conversation count (supports both column names)
    conv_col = None
    if 'conversations' in cols:
        conv_col = 'conversations'
    elif 'conversation_count' in cols:
        conv_col = 'conversation_count'

    if conv_col:
        ok &= df[conv_col].fillna(0) >= min_conv

    # Check for unique users
    if 'unique_users' in cols:
        ok &= df['unique_users'].fillna(0) >= min_users

    return df[ok].copy()

def assign_tier(aui: float, th: TierThresholds = TierThresholds()) -> str:
    if np.isnan(aui):
        return 'unknown'
    if aui < th.minimal:
        return 'below-min'
    if aui < th.emerging:
        return 'emerging'
    if aui < th.lower:
        return 'lower'
    if aui < th.upper:
        return 'upper'
    if aui <= th.leading:
        return 'leading'
    return 'outlier'

def _demo():
    """Run Taiwan regional AUI demo with realistic data."""
    print("Taiwan AI Usage Index (TAUI) - P3 Metrics Demo")
    print("=" * 50)

    # Generate demo data for Taiwan regions
    demo_data = generate_demo_data()
    print(f"生成的示範數據包含 {len(demo_data)} 個台灣地區")

    # Initialize AUI calculator
    calculator = AUICalculator(min_conversations=15, min_users=5)

    # Process the data
    results = calculator.process_data(demo_data)

    if results.empty:
        print("警告: 所有數據都被隱私過濾器移除")
        return

    print(f"\n隱私過濾後剩餘 {len(results)} 個地區")

    # Display results
    print("\nAUI 計算結果:")
    print("-" * 80)
    display_cols = ['region', 'aui_score', 'usage_tier', 'usage_percentage', 'working_age_percentage']
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.precision', 2)
    print(results[display_cols].to_string(index=False))

    # Save results
    output_path = 'data/processed/taiwan_aui_demo.csv'
    calculator.save_results(results, output_path)

    # Display summary statistics
    print(f"\n統計摘要:")
    print(f"平均 AUI 分數: {results['aui_score'].mean():.2f}")
    print(f"AUI 分數範圍: {results['aui_score'].min():.2f} - {results['aui_score'].max():.2f}")

    # Display tier distribution
    tier_counts = results['usage_tier'].value_counts()
    print(f"\n使用等級分佈:")
    for tier, count in tier_counts.items():
        print(f"  {tier}: {count} 個地區")


def main():
    """Main entry point for the AUI module."""
    parser = argparse.ArgumentParser(
        description="Taiwan AI Usage Index (TAUI) - P3 Metrics Calculator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例:
  python -m src.metrics.aui --demo     # 運行台灣地區示範模式
  python -m src.metrics.aui data.csv  # 處理實際數據文件
        """
    )

    parser.add_argument('--demo', action='store_true',
                       help='運行台灣地區示範模式並輸出到 data/processed/taiwan_aui_demo.csv')
    parser.add_argument('input_file', nargs='?',
                       help='輸入 CSV 文件路徑 (包含 region, conversation_count, unique_users, total_population, working_age_population 欄位)')
    parser.add_argument('--output', '-o', default='data/processed/aui_results.csv',
                       help='輸出 CSV 文件路徑 (預設: data/processed/aui_results.csv)')
    parser.add_argument('--min-conversations', type=int, default=15,
                       help='隱私過濾最小對話數 (預設: 15)')
    parser.add_argument('--min-users', type=int, default=5,
                       help='隱私過濾最小用戶數 (預設: 5)')

    args = parser.parse_args()

    if args.demo:
        _demo()
    elif args.input_file:
        # Process real data file
        try:
            data = pd.read_csv(args.input_file)
            calculator = AUICalculator(
                min_conversations=args.min_conversations,
                min_users=args.min_users
            )
            results = calculator.process_data(data)

            if results.empty:
                print("警告: 所有數據都被隱私過濾器移除")
                sys.exit(1)

            calculator.save_results(results, args.output)
            print(f"處理完成: {len(results)} 個地區的 AUI 分數已計算")

        except FileNotFoundError:
            print(f"錯誤: 找不到輸入文件 {args.input_file}")
            sys.exit(1)
        except Exception as e:
            print(f"錯誤: {e}")
            sys.exit(1)
    else:
        print("使用 --demo 參數來運行示範模式，或提供真實數據文件路徑")
        parser.print_help()


if __name__ == '__main__':
    main()
