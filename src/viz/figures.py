"""
Taiwan AI Usage Index (TAUI) - Visualization Module
Generates charts and figures for the Taiwan AI Usage Index report.
"""

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import seaborn as sns
from datetime import datetime
import warnings

# Suppress matplotlib warnings
warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')

# Set style for professional charts
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

class TAUIVisualizer:
    """Taiwan AI Usage Index visualization generator."""

    def __init__(self,
                 output_dir: str = "figures",
                 language: str = "zh-TW",
                 figure_size: Tuple[int, int] = (12, 8),
                 dpi: int = 300):
        """
        Initialize the TAUI visualizer.

        Args:
            output_dir: Directory to save figures
            language: Language for labels ('zh-TW' or 'en-US')
            figure_size: Default figure size (width, height)
            dpi: Figure resolution
        """
        self.output_dir = Path(output_dir)
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
        except (OSError, FileNotFoundError):
            # If we can't create the directory, fall back to current directory
            self.output_dir = Path.cwd() / "figures"
            self.output_dir.mkdir(parents=True, exist_ok=True)
        self.language = language
        self.figure_size = figure_size
        self.dpi = dpi

        # Setup fonts for Chinese characters
        self._setup_fonts()

        # Label translations
        self.labels = {
            'zh-TW': {
                'title_aui': '台灣AI使用指數 - 地區分布',
                'title_tier': 'AI使用層級分布',
                'title_trend': 'AI使用趨勢分析',
                'xlabel_regions': '地區',
                'ylabel_aui': 'AUI分數',
                'ylabel_percentage': '百分比 (%)',
                'xlabel_time': '時間',
                'tier_high': '高使用量',
                'tier_medium': '中使用量',
                'tier_low': '低使用量',
                'privacy_note': '註：遵循隱私保護原則，低於15次對話或5名用戶的數據已被排除',
                'data_source': '資料來源：台灣AI使用指數 (TAUI)',
                'generated_on': '生成時間：'
            },
            'en-US': {
                'title_aui': 'Taiwan AI Usage Index - Regional Distribution',
                'title_tier': 'AI Usage Tier Distribution',
                'title_trend': 'AI Usage Trend Analysis',
                'xlabel_regions': 'Regions',
                'ylabel_aui': 'AUI Score',
                'ylabel_percentage': 'Percentage (%)',
                'xlabel_time': 'Time',
                'tier_high': 'High Usage',
                'tier_medium': 'Medium Usage',
                'tier_low': 'Low Usage',
                'privacy_note': 'Note: Data with <15 conversations or <5 users excluded for privacy',
                'data_source': 'Data Source: Taiwan AI Usage Index (TAUI)',
                'generated_on': 'Generated on: '
            }
        }

    def _setup_fonts(self):
        """Setup fonts for Chinese text display."""
        try:
            # Try to find a Chinese font
            chinese_fonts = [
                'Microsoft JhengHei',  # Windows
                'PingFang TC',         # macOS
                'Noto Sans CJK TC',    # Linux
                'SimHei',              # Fallback
                'DejaVu Sans'          # Ultimate fallback
            ]

            for font_name in chinese_fonts:
                try:
                    plt.rcParams['font.sans-serif'] = [font_name]
                    plt.rcParams['axes.unicode_minus'] = False
                    # Test the font
                    fig, ax = plt.subplots(1, 1, figsize=(1, 1))
                    ax.text(0.5, 0.5, '測試', fontsize=10)
                    plt.close(fig)
                    break
                except:
                    continue
        except Exception:
            # Use default font if Chinese fonts fail
            plt.rcParams['font.sans-serif'] = ['DejaVu Sans']

    def _get_label(self, key: str) -> str:
        """Get label in the specified language."""
        # Handle invalid language by falling back to 'zh-TW' or returning the key
        if self.language not in self.labels:
            return key
        return self.labels[self.language].get(key, key)

    def create_aui_bar_chart(self,
                           data: pd.DataFrame,
                           save_as: str = "aui_regional_distribution.png") -> str:
        """
        Create bar chart showing AUI scores by Taiwan regions.

        Args:
            data: DataFrame with columns ['region', 'aui_score']
            save_as: Filename to save the chart

        Returns:
            Path to saved figure
        """
        fig, ax = plt.subplots(figsize=self.figure_size, dpi=self.dpi)

        # Sort data by AUI score for better visualization
        data_sorted = data.sort_values('aui_score', ascending=False)

        # Create bar chart
        bars = ax.bar(data_sorted['region'],
                     data_sorted['aui_score'],
                     color=sns.color_palette("viridis", len(data_sorted)),
                     alpha=0.8)

        # Customize chart
        ax.set_title(self._get_label('title_aui'), fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel(self._get_label('xlabel_regions'), fontsize=12)
        ax.set_ylabel(self._get_label('ylabel_aui'), fontsize=12)

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                   f'{height:.2f}', ha='center', va='bottom', fontsize=10)

        # Rotate x-axis labels if needed
        plt.xticks(rotation=45, ha='right')

        # Add grid for better readability
        ax.grid(True, alpha=0.3)
        ax.set_axisbelow(True)

        # Add footer with privacy note and data source
        fig.text(0.02, 0.02, self._get_label('privacy_note'), fontsize=8, alpha=0.7)
        fig.text(0.02, 0.005,
                f"{self._get_label('data_source')} | {self._get_label('generated_on')}{datetime.now().strftime('%Y-%m-%d')}",
                fontsize=8, alpha=0.7)

        plt.tight_layout()

        # Save figure
        output_path = self.output_dir / save_as
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()

        return str(output_path)

    def create_tier_pie_chart(self,
                            tier_data: Dict[str, int],
                            save_as: str = "usage_tier_distribution.png") -> str:
        """
        Create pie chart showing distribution of usage tiers.

        Args:
            tier_data: Dictionary with tier names and counts
            save_as: Filename to save the chart

        Returns:
            Path to saved figure
        """
        fig, ax = plt.subplots(figsize=self.figure_size, dpi=self.dpi)

        # Prepare data
        tier_mapping = {
            'high': self._get_label('tier_high'),
            'medium': self._get_label('tier_medium'),
            'low': self._get_label('tier_low')
        }

        labels = [tier_mapping.get(tier, tier) for tier in tier_data.keys()]
        sizes = list(tier_data.values())
        colors = ['#ff6b6b', '#4ecdc4', '#45b7d1']

        # Create pie chart
        wedges, texts, autotexts = ax.pie(sizes,
                                         labels=labels,
                                         colors=colors,
                                         autopct='%1.1f%%',
                                         startangle=90,
                                         explode=(0.05, 0.05, 0.05))

        # Enhance text appearance
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(12)

        for text in texts:
            text.set_fontsize(12)
            text.set_fontweight('bold')

        ax.set_title(self._get_label('title_tier'), fontsize=16, fontweight='bold', pad=20)

        # Add footer
        fig.text(0.02, 0.02, self._get_label('privacy_note'), fontsize=8, alpha=0.7)
        fig.text(0.02, 0.005,
                f"{self._get_label('data_source')} | {self._get_label('generated_on')}{datetime.now().strftime('%Y-%m-%d')}",
                fontsize=8, alpha=0.7)

        plt.tight_layout()

        # Save figure
        output_path = self.output_dir / save_as
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()

        return str(output_path)

    def create_trend_line_chart(self,
                              trend_data: pd.DataFrame,
                              save_as: str = "usage_trend_analysis.png") -> str:
        """
        Create line chart showing AI usage trends over time.

        Args:
            trend_data: DataFrame with columns ['date', 'aui_score', 'region'] (optional)
            save_as: Filename to save the chart

        Returns:
            Path to saved figure
        """
        fig, ax = plt.subplots(figsize=self.figure_size, dpi=self.dpi)

        # Check if regional breakdown exists
        if 'region' in trend_data.columns:
            # Plot by region
            for region in trend_data['region'].unique():
                region_data = trend_data[trend_data['region'] == region]
                ax.plot(region_data['date'], region_data['aui_score'],
                       marker='o', linewidth=2, label=region)
            ax.legend()
        else:
            # Single trend line
            ax.plot(trend_data['date'], trend_data['aui_score'],
                   marker='o', linewidth=3, color='#2E86AB')

        # Customize chart
        ax.set_title(self._get_label('title_trend'), fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel(self._get_label('xlabel_time'), fontsize=12)
        ax.set_ylabel(self._get_label('ylabel_aui'), fontsize=12)

        # Format dates on x-axis
        plt.xticks(rotation=45)

        # Add grid
        ax.grid(True, alpha=0.3)
        ax.set_axisbelow(True)

        # Add footer
        fig.text(0.02, 0.02, self._get_label('privacy_note'), fontsize=8, alpha=0.7)
        fig.text(0.02, 0.005,
                f"{self._get_label('data_source')} | {self._get_label('generated_on')}{datetime.now().strftime('%Y-%m-%d')}",
                fontsize=8, alpha=0.7)

        plt.tight_layout()

        # Save figure
        output_path = self.output_dir / save_as
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()

        return str(output_path)

    def generate_all_charts(self,
                          aui_data: Optional[pd.DataFrame] = None,
                          tier_data: Optional[Dict[str, int]] = None,
                          trend_data: Optional[pd.DataFrame] = None) -> Dict[str, str]:
        """
        Generate all charts with sample data if not provided.

        Args:
            aui_data: Regional AUI data
            tier_data: Usage tier distribution
            trend_data: Time series trend data

        Returns:
            Dictionary mapping chart types to file paths
        """
        chart_paths = {}

        # Generate AUI bar chart
        if aui_data is None:
            # Sample data for Taiwan regions
            aui_data = pd.DataFrame({
                'region': ['台北市', '新北市', '桃園市', '台中市', '台南市', '高雄市', '新竹市', '基隆市'],
                'aui_score': [0.85, 0.78, 0.72, 0.69, 0.65, 0.71, 0.82, 0.58]
            })

        chart_paths['aui_bar'] = self.create_aui_bar_chart(aui_data)

        # Generate tier pie chart
        if tier_data is None:
            tier_data = {'high': 35, 'medium': 45, 'low': 20}

        chart_paths['tier_pie'] = self.create_tier_pie_chart(tier_data)

        # Generate trend line chart
        if trend_data is None:
            # Sample trend data
            dates = pd.date_range('2024-01-01', periods=12, freq='M')
            trend_data = pd.DataFrame({
                'date': dates,
                'aui_score': np.random.normal(0.7, 0.1, 12).clip(0, 1)
            })

        chart_paths['trend_line'] = self.create_trend_line_chart(trend_data)

        return chart_paths


def main():
    """Main function to generate all visualizations."""
    print("Generating TAUI visualizations...")

    # Initialize visualizer for both languages
    visualizers = {
        'zh-TW': TAUIVisualizer(language='zh-TW'),
        'en-US': TAUIVisualizer(language='en-US')
    }

    all_paths = {}

    for lang, viz in visualizers.items():
        print(f"Creating {lang} charts...")

        # Generate all charts
        chart_paths = viz.generate_all_charts()

        # Rename files to include language
        lang_paths = {}
        for chart_type, path in chart_paths.items():
            path_obj = Path(path)
            new_name = f"{path_obj.stem}_{lang}{path_obj.suffix}"
            new_path = path_obj.parent / new_name
            Path(path).rename(new_path)
            lang_paths[chart_type] = str(new_path)

        all_paths[lang] = lang_paths

    print("All visualizations generated successfully!")
    print("\nGenerated files:")
    for lang, paths in all_paths.items():
        print(f"\n{lang}:")
        for chart_type, path in paths.items():
            print(f"  - {chart_type}: {path}")

    return all_paths


if __name__ == "__main__":
    main()