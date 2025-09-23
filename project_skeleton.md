taiwan-ai-usage-index/
├─ README.md                    # 專案說明與快速開始
├─ CLAUDE.md                    # Claude Code 的工作規範（TDD/隱私/工具白名單）
├─ requirements.txt             # 依賴：pandas/numpy/scipy/pydantic/matplotlib/pyarrow/pytest
├─ Makefile                     # 常用工作流：init/test/figures/report
├─ prompts/
│  ├─ task_labeler.md          # 任務 → O*NET/SOC 頂層分類 few-shot 模板
│  └─ mode_labeler.md          # 合作模式（automation/augmentation）few-shot 模板
├─ src/
│  ├─ ingest/
│  │  ├─ validate.py           # Pydantic 結構，規範資料欄位
│  │  └─ anthropic_open_data.py# 讀取 open CSV、篩選 TWN 與同儕、寫 Parquet
│  ├─ labeling/
│  │  ├─ interface.py          # 介面定義（供 Claude Code 注入/替換）
│  │  ├─ onets.py              # 任務分類器（LLM hook；測試可 patch）
│  │  └─ mode.py               # 合作模式分類器（LLM hook）
│  ├─ metrics/
│  │  └─ aui.py                # AUI 計算、隱私門檻濾除、Tier 區間；含 --demo
│  ├─ viz/
│  │  └─ figures.py            # AUI 長條、AUI~GDP 散點（log-log）等圖
│  └─ report/
│     └─ make_report.py        # 產出 Markdown 報告（demo 或實數據）
├─ tests/
│  ├─ test_aui.py              # AUI 比例邏輯、隱私門檻、Tier 邊界測試
│  └─ test_labelers.py         # Labeler 回傳 shape 測試（可注入假回覆）
├─ data/
│  ├─ raw/.gitkeep             # 原始資料（不進版控，勿放個資）
│  ├─ interim/.gitkeep         # 清理後中繼
│  └─ processed/
│     ├─ .gitkeep
│     └─ gdp_demo.csv          # 小示例（繪圖用）
├─ figures/.gitkeep
└─ report/.gitkeep
