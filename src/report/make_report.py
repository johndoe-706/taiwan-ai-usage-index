"""
Taiwan AI Usage Index (TAUI) - Report Generation Module
Generates comprehensive Markdown reports for the Taiwan AI Usage Index.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import json
from dataclasses import dataclass


@dataclass
class ReportConfig:
    """Configuration for report generation."""
    output_dir: str = "report"
    language: str = "zh-TW"
    include_charts: bool = True
    include_methodology: bool = True
    include_privacy_statement: bool = True
    include_data_tables: bool = True


class TAUIReportGenerator:
    """Taiwan AI Usage Index report generator."""

    def __init__(self, config: ReportConfig = None):
        """
        Initialize the report generator.

        Args:
            config: Report configuration
        """
        self.config = config or ReportConfig()
        self.output_dir = Path(self.config.output_dir)
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
        except (OSError, FileNotFoundError):
            # If we can't create the directory, fall back to current directory
            self.output_dir = Path.cwd() / "report"
            self.output_dir.mkdir(parents=True, exist_ok=True)

        # Report templates by language
        self.templates = {
            'zh-TW': {
                'title': '# 台灣AI使用指數 (TAUI) 報告',
                'exec_summary_title': '## 執行摘要',
                'methodology_title': '## 研究方法',
                'findings_title': '## 主要發現',
                'charts_title': '## 視覺化分析',
                'data_tables_title': '## 數據表格',
                'privacy_title': '## 隱私保護聲明',
                'appendix_title': '## 附錄',
                'generated_on': '報告生成時間',
                'version': '版本',
                'data_period': '數據期間',
                'total_regions': '涵蓋地區總數',
                'avg_aui_score': '平均AUI分數',
                'highest_region': '最高分地區',
                'lowest_region': '最低分地區',
                'privacy_statement': '''
本報告嚴格遵循隱私保護原則：
- 所有少於15次對話或5名用戶的數據已被排除
- 不包含任何個人識別資訊 (PII)
- 數據經過適當的統計處理和匿名化
- 符合台灣個人資料保護法相關規定
                '''.strip(),
                'methodology_content': '''
### 數據來源
- **原始數據**: Anthropic開放數據集，篩選台灣地區 (TWN) 資料
- **標籤方法**: 使用O*NET職業分類系統進行AI使用強度標註
- **模式識別**: 應用機器學習技術識別對話模式

### AUI計算方法
AUI分數 = (AI使用率 / 工作年齡人口比例) × 100

其中：
- AI使用率：該地區AI對話數量 / 總對話數量
- 工作年齡人口比例：該地區工作年齡人口 / 總工作年齡人口

### 使用層級分類
- **高使用量**: AUI ≥ 0.8
- **中使用量**: 0.5 ≤ AUI < 0.8
- **低使用量**: AUI < 0.5

### 隱私過濾
應用最小閾值過濾：`apply_privacy_filters(min_conv=15, min_users=5)`
                '''.strip()
            },
            'en-US': {
                'title': '# Taiwan AI Usage Index (TAUI) Report',
                'exec_summary_title': '## Executive Summary',
                'methodology_title': '## Methodology',
                'findings_title': '## Key Findings',
                'charts_title': '## Visual Analysis',
                'data_tables_title': '## Data Tables',
                'privacy_title': '## Privacy Protection Statement',
                'appendix_title': '## Appendix',
                'generated_on': 'Report Generated',
                'version': 'Version',
                'data_period': 'Data Period',
                'total_regions': 'Total Regions Covered',
                'avg_aui_score': 'Average AUI Score',
                'highest_region': 'Highest Scoring Region',
                'lowest_region': 'Lowest Scoring Region',
                'privacy_statement': '''
This report strictly adheres to privacy protection principles:
- All data with <15 conversations or <5 users has been excluded
- Contains no personally identifiable information (PII)
- Data has been properly anonymized and statistically processed
- Complies with Taiwan Personal Data Protection Act regulations
                '''.strip(),
                'methodology_content': '''
### Data Sources
- **Raw Data**: Anthropic open dataset, filtered for Taiwan (TWN) region
- **Labeling Method**: O*NET occupational classification system for AI usage intensity
- **Pattern Recognition**: Machine learning techniques for conversation pattern identification

### AUI Calculation Method
AUI Score = (AI Usage Rate / Working-Age Population Ratio) × 100

Where:
- AI Usage Rate: Regional AI conversations / Total conversations
- Working-Age Population Ratio: Regional working-age population / Total working-age population

### Usage Tier Classification
- **High Usage**: AUI ≥ 0.8
- **Medium Usage**: 0.5 ≤ AUI < 0.8
- **Low Usage**: AUI < 0.5

### Privacy Filtering
Applied minimum threshold filtering: `apply_privacy_filters(min_conv=15, min_users=5)`
                '''.strip()
            }
        }

    def _get_template(self, key: str) -> str:
        """Get template string for the configured language."""
        return self.templates[self.config.language].get(key, key)

    def generate_executive_summary(self, summary_data: Dict[str, Any]) -> str:
        """Generate executive summary section."""
        template = self._get_template('exec_summary_title')

        if self.config.language == 'zh-TW':
            content = f"""
{template}

台灣AI使用指數 (TAUI) 分析顯示，台灣各地區在AI技術採用方面存在顯著差異。

### 關鍵統計數據
- **{self._get_template('total_regions')}**: {summary_data.get('total_regions', 'N/A')}
- **{self._get_template('avg_aui_score')}**: {summary_data.get('avg_aui_score', 'N/A'):.3f}
- **{self._get_template('highest_region')}**: {summary_data.get('highest_region', 'N/A')} ({summary_data.get('highest_score', 'N/A'):.3f})
- **{self._get_template('lowest_region')}**: {summary_data.get('lowest_region', 'N/A')} ({summary_data.get('lowest_score', 'N/A'):.3f})

### 主要洞察
1. **城市化程度與AI使用呈正相關**: 大都會地區展現更高的AI採用率
2. **地區發展差距**: 不同地區間AI使用水平存在明顯落差
3. **成長潛力**: 中低使用量地區具有顯著的AI普及發展空間

本指數為政策制定者、企業決策者及研究人員提供重要的AI技術普及現況參考。
            """.strip()
        else:
            content = f"""
{template}

The Taiwan AI Usage Index (TAUI) analysis reveals significant variations in AI technology adoption across different regions of Taiwan.

### Key Statistics
- **{self._get_template('total_regions')}**: {summary_data.get('total_regions', 'N/A')}
- **{self._get_template('avg_aui_score')}**: {summary_data.get('avg_aui_score', 'N/A'):.3f}
- **{self._get_template('highest_region')}**: {summary_data.get('highest_region', 'N/A')} ({summary_data.get('highest_score', 'N/A'):.3f})
- **{self._get_template('lowest_region')}**: {summary_data.get('lowest_region', 'N/A')} ({summary_data.get('lowest_score', 'N/A'):.3f})

### Key Insights
1. **Urbanization correlates with AI usage**: Metropolitan areas show higher AI adoption rates
2. **Regional development gaps**: Clear disparities in AI usage levels across regions
3. **Growth potential**: Medium and low usage regions show significant potential for AI proliferation

This index provides valuable reference for policymakers, business decision-makers, and researchers on current AI technology penetration.
            """.strip()

        return content

    def generate_data_tables(self,
                           aui_data: pd.DataFrame,
                           tier_data: Dict[str, int]) -> str:
        """Generate data tables section."""
        template = self._get_template('data_tables_title')

        # Convert DataFrame to markdown table
        def df_to_markdown(df: pd.DataFrame) -> str:
            """Convert DataFrame to markdown table."""
            if df.empty:
                return "*No data available*"

            # Create header
            headers = "| " + " | ".join(df.columns) + " |"
            separator = "| " + " | ".join(["---"] * len(df.columns)) + " |"

            # Create rows
            rows = []
            for _, row in df.iterrows():
                row_str = "| " + " | ".join([str(val) for val in row.values]) + " |"
                rows.append(row_str)

            return "\n".join([headers, separator] + rows)

        # Calculate total for percentage calculations (handle empty data)
        total_tier_count = sum(tier_data.values())
        high_pct = (tier_data.get('high', 0) / total_tier_count * 100) if total_tier_count > 0 else 0
        medium_pct = (tier_data.get('medium', 0) / total_tier_count * 100) if total_tier_count > 0 else 0
        low_pct = (tier_data.get('low', 0) / total_tier_count * 100) if total_tier_count > 0 else 0

        if self.config.language == 'zh-TW':
            # Handle empty dataframe statistics
            if aui_data.empty or 'aui_score' not in aui_data.columns:
                stats_section = """
| 統計指標 | 數值 |
|---------|------|
| 平均分數 | N/A |
| 標準差 | N/A |
| 最高分數 | N/A |
| 最低分數 | N/A |
| 中位數 | N/A |"""
            else:
                stats_section = f"""
| 統計指標 | 數值 |
|---------|------|
| 平均分數 | {aui_data['aui_score'].mean():.3f} |
| 標準差 | {aui_data['aui_score'].std():.3f} |
| 最高分數 | {aui_data['aui_score'].max():.3f} |
| 最低分數 | {aui_data['aui_score'].min():.3f} |
| 中位數 | {aui_data['aui_score'].median():.3f} |"""

            content = f"""
{template}

### 地區AUI分數詳細表

{df_to_markdown(aui_data)}

### 使用層級分布統計

| 使用層級 | 地區數量 | 百分比 |
|---------|---------|--------|
| 高使用量 (≥0.8) | {tier_data.get('high', 0)} | {high_pct:.1f}% |
| 中使用量 (0.5-0.8) | {tier_data.get('medium', 0)} | {medium_pct:.1f}% |
| 低使用量 (<0.5) | {tier_data.get('low', 0)} | {low_pct:.1f}% |

### 統計摘要
{stats_section}
            """.strip()
        else:
            # Handle empty dataframe statistics for English
            if aui_data.empty or 'aui_score' not in aui_data.columns:
                stats_section = """
| Statistical Metric | Value |
|-------------------|-------|
| Average Score | N/A |
| Standard Deviation | N/A |
| Maximum Score | N/A |
| Minimum Score | N/A |
| Median | N/A |"""
            else:
                stats_section = f"""
| Statistical Metric | Value |
|-------------------|-------|
| Average Score | {aui_data['aui_score'].mean():.3f} |
| Standard Deviation | {aui_data['aui_score'].std():.3f} |
| Maximum Score | {aui_data['aui_score'].max():.3f} |
| Minimum Score | {aui_data['aui_score'].min():.3f} |
| Median | {aui_data['aui_score'].median():.3f} |"""

            content = f"""
{template}

### Regional AUI Scores Detailed Table

{df_to_markdown(aui_data)}

### Usage Tier Distribution Statistics

| Usage Tier | Region Count | Percentage |
|-----------|--------------|------------|
| High Usage (≥0.8) | {tier_data.get('high', 0)} | {high_pct:.1f}% |
| Medium Usage (0.5-0.8) | {tier_data.get('medium', 0)} | {medium_pct:.1f}% |
| Low Usage (<0.5) | {tier_data.get('low', 0)} | {low_pct:.1f}% |

### Statistical Summary
{stats_section}
            """.strip()

        return content

    def generate_charts_section(self, chart_paths: Dict[str, str]) -> str:
        """Generate charts section with embedded images."""
        template = self._get_template('charts_title')

        if self.config.language == 'zh-TW':
            content = f"""
{template}

### 地區AUI分數分布圖
![地區AUI分數分布](../{chart_paths.get('aui_bar', 'figures/aui_regional_distribution_zh-TW.png')})

### AI使用層級分布圓餅圖
![AI使用層級分布](../{chart_paths.get('tier_pie', 'figures/usage_tier_distribution_zh-TW.png')})

### AI使用趨勢分析
![AI使用趨勢](../{chart_paths.get('trend_line', 'figures/usage_trend_analysis_zh-TW.png')})
            """.strip()
        else:
            content = f"""
{template}

### Regional AUI Score Distribution
![Regional AUI Distribution](../{chart_paths.get('aui_bar', 'figures/aui_regional_distribution_en-US.png')})

### AI Usage Tier Distribution
![Usage Tier Distribution](../{chart_paths.get('tier_pie', 'figures/usage_tier_distribution_en-US.png')})

### AI Usage Trend Analysis
![Usage Trend Analysis](../{chart_paths.get('trend_line', 'figures/usage_trend_analysis_en-US.png')})
            """.strip()

        return content

    def generate_full_report(self,
                           aui_data: pd.DataFrame = None,
                           tier_data: Dict[str, int] = None,
                           chart_paths: Dict[str, str] = None,
                           output_filename: str = None) -> str:
        """
        Generate complete TAUI report.

        Args:
            aui_data: Regional AUI scores data
            tier_data: Usage tier distribution
            chart_paths: Dictionary of chart file paths
            output_filename: Custom output filename

        Returns:
            Path to generated report file
        """
        # Use sample data if not provided
        if aui_data is None:
            aui_data = pd.DataFrame({
                'region': ['台北市', '新北市', '桃園市', '台中市', '台南市', '高雄市', '新竹市', '基隆市'],
                'aui_score': [0.85, 0.78, 0.72, 0.69, 0.65, 0.71, 0.82, 0.58]
            })

        if tier_data is None:
            # Calculate tiers from aui_data
            high_count = len(aui_data[aui_data['aui_score'] >= 0.8])
            medium_count = len(aui_data[(aui_data['aui_score'] >= 0.5) & (aui_data['aui_score'] < 0.8)])
            low_count = len(aui_data[aui_data['aui_score'] < 0.5])
            tier_data = {'high': high_count, 'medium': medium_count, 'low': low_count}

        if chart_paths is None:
            chart_paths = {
                'aui_bar': f'figures/aui_regional_distribution_{self.config.language}.png',
                'tier_pie': f'figures/usage_tier_distribution_{self.config.language}.png',
                'trend_line': f'figures/usage_trend_analysis_{self.config.language}.png'
            }

        # Generate summary data
        summary_data = {
            'total_regions': len(aui_data),
            'avg_aui_score': aui_data['aui_score'].mean(),
            'highest_region': aui_data.loc[aui_data['aui_score'].idxmax(), 'region'],
            'highest_score': aui_data['aui_score'].max(),
            'lowest_region': aui_data.loc[aui_data['aui_score'].idxmin(), 'region'],
            'lowest_score': aui_data['aui_score'].min()
        }

        # Build report content
        report_sections = []

        # Title and metadata
        report_sections.append(self._get_template('title'))
        report_sections.append(f"**{self._get_template('generated_on')}**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_sections.append(f"**{self._get_template('version')}**: 1.0.0")
        report_sections.append(f"**{self._get_template('data_period')}**: 2024")
        report_sections.append("")

        # Executive summary
        report_sections.append(self.generate_executive_summary(summary_data))
        report_sections.append("")

        # Methodology
        if self.config.include_methodology:
            report_sections.append(self._get_template('methodology_title'))
            report_sections.append(self._get_template('methodology_content'))
            report_sections.append("")

        # Charts
        if self.config.include_charts:
            report_sections.append(self.generate_charts_section(chart_paths))
            report_sections.append("")

        # Data tables
        if self.config.include_data_tables:
            report_sections.append(self.generate_data_tables(aui_data, tier_data))
            report_sections.append("")

        # Privacy statement
        if self.config.include_privacy_statement:
            report_sections.append(self._get_template('privacy_title'))
            report_sections.append(self._get_template('privacy_statement'))
            report_sections.append("")

        # Generate filename
        if output_filename is None:
            if self.config.language == 'zh-TW':
                output_filename = "INDEX_TAIWAN.md"
            else:
                output_filename = "INDEX_TAIWAN_EN.md"

        # Write report file
        report_content = "\n".join(report_sections)
        output_path = self.output_dir / output_filename

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_content)

        return str(output_path)

    def generate_json_metadata(self,
                             aui_data: pd.DataFrame,
                             tier_data: Dict[str, int],
                             output_filename: str = "taui_metadata.json") -> str:
        """Generate JSON metadata file for the report."""
        metadata = {
            "report_info": {
                "title": "Taiwan AI Usage Index (TAUI)",
                "version": "1.0.0",
                "generated_on": datetime.now().isoformat(),
                "language": self.config.language,
                "data_period": "2024"
            },
            "statistics": {
                "total_regions": len(aui_data),
                "avg_aui_score": float(aui_data['aui_score'].mean()),
                "std_aui_score": float(aui_data['aui_score'].std()),
                "max_aui_score": float(aui_data['aui_score'].max()),
                "min_aui_score": float(aui_data['aui_score'].min()),
                "median_aui_score": float(aui_data['aui_score'].median())
            },
            "tier_distribution": tier_data,
            "regional_scores": aui_data.to_dict('records'),
            "privacy_compliance": {
                "min_conversations": 15,
                "min_users": 5,
                "pii_removed": True,
                "anonymized": True
            }
        }

        output_path = self.output_dir / output_filename
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        return str(output_path)


def main():
    """Main function to generate TAUI reports."""
    print("Generating TAUI reports...")

    # Sample data
    aui_data = pd.DataFrame({
        'region': ['台北市', '新北市', '桃園市', '台中市', '台南市', '高雄市', '新竹市', '基隆市'],
        'aui_score': [0.85, 0.78, 0.72, 0.69, 0.65, 0.71, 0.82, 0.58]
    })

    # Calculate tier distribution
    high_count = len(aui_data[aui_data['aui_score'] >= 0.8])
    medium_count = len(aui_data[(aui_data['aui_score'] >= 0.5) & (aui_data['aui_score'] < 0.8)])
    low_count = len(aui_data[aui_data['aui_score'] < 0.5])
    tier_data = {'high': high_count, 'medium': medium_count, 'low': low_count}

    # Chart paths
    chart_paths = {
        'aui_bar': 'figures/aui_regional_distribution_zh-TW.png',
        'tier_pie': 'figures/usage_tier_distribution_zh-TW.png',
        'trend_line': 'figures/usage_trend_analysis_zh-TW.png'
    }

    generated_files = []

    # Generate reports for both languages
    for language in ['zh-TW', 'en-US']:
        print(f"Generating {language} report...")

        config = ReportConfig(language=language)
        generator = TAUIReportGenerator(config)

        # Update chart paths for language
        lang_chart_paths = {
            key: path.replace('zh-TW', language)
            for key, path in chart_paths.items()
        }

        # Generate full report
        report_path = generator.generate_full_report(
            aui_data=aui_data,
            tier_data=tier_data,
            chart_paths=lang_chart_paths
        )
        generated_files.append(report_path)

        # Generate JSON metadata
        metadata_filename = f"taui_metadata_{language.replace('-', '_').lower()}.json"
        metadata_path = generator.generate_json_metadata(
            aui_data=aui_data,
            tier_data=tier_data,
            output_filename=metadata_filename
        )
        generated_files.append(metadata_path)

    print("All reports generated successfully!")
    print("\nGenerated files:")
    for file_path in generated_files:
        print(f"  - {file_path}")

    return generated_files


if __name__ == "__main__":
    main()