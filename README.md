# 🇹🇼 Taiwan AI Usage Index (TAUI)

[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-117%2F122%20passing-brightgreen)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-95.9%25-brightgreen)](tests/)

Taiwan AI Usage Index (TAUI) 是一個開源的資料分析框架，用於測量和分析台灣各地區的 AI 技術採用率。本專案參考 Anthropic Economic Index 方法論，專為台灣本地化需求設計。

[English](#english) | [中文](#中文)

## 中文

### 🎯 專案特色

- **區域 AI 使用指數計算** - 量化各地區 AI 採用程度 (AUI = 使用率 / 工作年齡人口比例)
- **隱私保護機制** - 自動過濾低於閾值的數據 (< 15 對話或 < 5 使用者)
- **O*NET 職業分類** - 自動分類 AI 使用任務類型
- **協作模式識別** - 分析人機協作模式 (自動化 vs 增強)
- **視覺化報告** - 自動生成圖表與分析報告
- **雙語支援** - 中英文報告與視覺化
- **TDD 開發** - 122 個測試案例，95.9% 覆蓋率

### 🚀 快速開始

```bash
# 1) Clone 專案
git clone https://github.com/thc1006/taiwan-ai-usage-index.git
cd taiwan-ai-usage-index

# 2) 安裝相依套件
python3 -m venv .venv && source .venv/bin/activate  # Linux/Mac
# 或 Windows: python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt

# 3) 執行測試確認安裝
pytest -q

# 4) 執行示範模式
python -m src.metrics.aui --demo

# 5) 生成圖表與報告
python -m src.viz.figures
python -m src.report.make_report
```

### 📊 資料處理管線

```python
from src.ingest import process_anthropic_data
from src.labeling import classify_task_llm, classify_mode_llm
from src.metrics import AUICalculator

# 1. 資料擷取與篩選 (台灣同儕國家: TWN, SGP, KOR, JPN, HKG)
df = process_anthropic_data(
    'data/raw/anthropic_open/conversations.csv',
    'data/interim/open/taiwan_filtered.parquet'
)

# 2. 任務分類 (O*NET/SOC)
df['task_category'] = df['summary'].apply(classify_task_llm)

# 3. 協作模式分類
df['collab_mode'] = df['summary'].apply(classify_mode_llm)

# 4. 計算 AUI 指數
calculator = AUICalculator(min_conversations=15, min_users=5)
results = calculator.process_data(df)
calculator.save_results(results, 'output/aui_results.csv')
```

### 📁 專案結構

```
taiwan-ai-usage-index/
├── src/
│   ├── ingest/          # 資料擷取模組 (CSV → Parquet)
│   ├── labeling/        # 分類標註模組 (O*NET, 協作模式)
│   ├── metrics/         # AUI 計算模組
│   ├── viz/             # 視覺化模組 (Matplotlib/Seaborn)
│   └── report/          # 報告生成模組 (Markdown/JSON)
├── tests/               # 測試套件 (122 個測試)
├── prompts/             # Few-shot 提示範本
├── data/
│   ├── raw/            # 原始資料 (不納入版控)
│   ├── interim/        # 中間處理資料
│   └── processed/      # 最終資料
├── figures/            # 生成圖表
├── report/             # 分析報告
└── ci/                 # CI/CD 工作流程
```

---

## English

### 🎯 Features

- **Regional AI Usage Index** - Quantify AI adoption across Taiwan regions
- **Privacy Protection** - Auto-filter data below thresholds (<15 conversations or <5 users)
- **O*NET Classification** - Automatic task categorization using occupational taxonomy
- **Collaboration Mode Detection** - Analyze human-AI interaction patterns (automation vs augmentation)
- **Visual Reports** - Auto-generated charts and analysis reports
- **Bilingual Support** - Chinese and English reports
- **TDD Development** - 122 test cases with 95.9% coverage

### 🚀 Quick Start

```bash
# 1) Clone repository
git clone https://github.com/thc1006/taiwan-ai-usage-index.git
cd taiwan-ai-usage-index

# 2) Install dependencies
python3 -m venv .venv && source .venv/bin/activate  # Linux/Mac
# or Windows: python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt

# 3) Run tests to verify installation
pytest -q

# 4) Run demo mode
python -m src.metrics.aui --demo

# 5) Generate visualizations and report
python -m src.viz.figures
python -m src.report.make_report
```

### 📈 AUI Calculation Method

```
AUI = (Regional AI Usage Rate / Regional Working-Age Population Ratio) × 100
```

Usage Tiers:
- **High Usage**: AUI ≥ 100
- **Medium Usage**: 50 ≤ AUI < 100
- **Low Usage**: AUI < 50

### 🔬 Research Applications

- **Policy Research** - Understand AI adoption patterns for policy making
- **Market Analysis** - Assess regional AI maturity for business strategy
- **Academic Studies** - Research human-AI collaboration patterns
- **Social Impact** - Analyze digital divide and technology adoption

### 🤝 Contributing

We welcome contributions! Please follow TDD principles and ensure tests pass before submitting PRs.

### 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

### 📚 Citation

```bibtex
@software{taui2025,
  title = {Taiwan AI Usage Index (TAUI)},
  author = {THC1006},
  year = {2025},
  url = {https://github.com/thc1006/taiwan-ai-usage-index}
}
```

### 📮 Contact

- **Issues**: [GitHub Issues](https://github.com/thc1006/taiwan-ai-usage-index/issues)
- **Discussions**: [GitHub Discussions](https://github.com/thc1006/taiwan-ai-usage-index/discussions)

---

## Notes
- This repo is scaffolding for research reproducibility. Replace/extend sample data with your own **de-identified** volunteer data or open data slices.
- Avoid committing PII. The tests enforce privacy filtering behavior.

## cite
```
@online{appelmccrorytamkin2025geoapi,

author = {Ruth Appel and Peter McCrory and Alex Tamkin and Michael Stern and Miles McCain and Tyler Neylon],

title = {Anthropic Economic Index report: Uneven geographic and enterprise AI adoption},

date = {2025-09-15},

year = {2025},

url = {www.anthropic.com/research/anthropic-economic-index-september-2025-report},

}
```
