# TDD 任務分解（每階段可直接貼給 Claude Code 的提示詞）

> 格式慣例：先「計畫 → 測試 → 實作 → 驗收」，禁止硬編密鑰；工具白名單；產出路徑固定。

## P0｜專案腳手架與基礎測試

**提示詞：**
「你是*資深研究工程師*。請依下列規則建立骨架：

1. 先列出落地計畫與檔案樹，再生成檔案。2) 嚴格 TDD：先寫 `tests/`，再最小實作。3) 只用白名單工具（bash, git, python, pip/uv, jq, sed, awk, pytest, matplotlib）。4) 不得寫入雲端或上傳資料。5) 產出路徑固定於上述樹。請建立：

* `pyproject.toml` 或 `requirements.txt`（pandas, numpy, scipy, matplotlib, pytest, pydantic, unidecode）。
* `src/ingest/validate.py`（schema 驗證 stub），`src/metrics/aui.py`（AUI 函式 stub），`src/labeling/interface.py`（介面 stub）。
* `tests/test_aui.py`（AUI 定義單元測試：AUI>1/<1 案例）、`tests/test_privacy.py`（<15/<5 門檻濾除）。
  產出後自動執行 pytest，修到全綠，最後 `git init` 並建立第一個乾淨提交。」

## P1｜資料匯入與去識別

**提示詞：**
「新增 `src/ingest/anthropic_open_data.py`，輸入：`data/raw/anthropic_open/*.csv`，輸出：`data/interim/open/claude_ai_by_country.parquet`。需求：

* 只保留 `country_code`, `dt`, `task_text`/`task_id`, `collab_mode`（若有），`count`。
* 濾國碼 `TWN` 與同儕清單（SGP, AUS, NZL, KOR 等）。
* 增加欄位 `period='2025-08-04/11'` 作為視窗註記。
* 單元測試：當輸入 CSV 有雜訊列時，清理後行數與欄位型別符合預期；空值/錯碼自動丟棄或回報。
  實作後跑 pytest，產出中繼檔到 `data/interim/open/`，不可 commit 原始資料。」

## P1｜匯入開放資料（TWN 子集）

**貼給 Claude Code 的提示詞**：

> 你是資深資料工程師。請在不新增外部依賴的前提下，完成 `src/ingest/anthropic_open_data.py` 的 CLI 流程：
>
> 1. 讀取 `data/raw/anthropic_open/*.csv` 的欄位（至少含 `country_code, dt, task_text/task_id, collab_mode, count`）。
> 2. 僅保留 `TWN` 與同儕國家（SGP/AUS/NZL/KOR/JPN/HKG/USA/CAN/GBR/DEU/FRA）。
> 3. 產出 `data/interim/open/claude_ai_by_country.parquet`（以 pyarrow 寫入）。
> 4. 若 CSV 欄位雜訊，請寬鬆容錯並記錄移除的列數。
> 5. 撰寫對應單元測試（若必要可新增 `tests/test_ingest.py`），覆蓋：缺欄位、空集、雜訊行。
>    請直接修改檔案與新增測試，最後執行 `pytest -q`，直到全綠。

## P2｜任務/合作模式標註器（few-shot）

**提示詞：**
「建立 `prompts/task_labeler.md` 與 `prompts/mode_labeler.md`（中英雙語），規範：

* 任務對齊 O\*NET/SOC：回 `top_category`（如 Computer & Mathematical）、`task_code`（可空）、`confidence`。
* 合作模式：`automation` vs `augmentation`（各自對應子類：directive/learning/iteration/validation），回主模式與比例。
* 產出 `src/labeling/onets.py` 與 `src/labeling/mode.py`：包裝 LLM 調用（以函式接口抽象，測試時可注入假回應）。
* 單元測試以假 LLM 回應驗證：輸入 5 條合成對話，分類穩定、可重現（設 random seed）。
* 建 `tests/test_labelers.py`。完成後 pytest 全綠。」

## P2｜Few-shot 任務分類（O\*NET/SOC）

**提示詞**：

> 你是任務分類器的實作者。請依 `prompts/task_labeler.md` 的規格：
>
> * 新增 `src/labeling/onets.py` 中的 `classify_task_llm(text:str)->dict` 具體實作（以你在 Claude Code 的少樣例推斷）。
> * 保證輸出鍵：`top_category, task_code, confidence, rationale`，並在低信心時回 `Unknown`。
> * 更新 `tests/test_labelers.py`，新增 5 條多樣化測資（教育/財務/科研/寫程式/行政），只驗證**鍵存在與型別**，不鎖定類別值。
> * 不得上傳/存任何個資；不得呼叫外網。
> * 完成後跑 `pytest -q`。

## P3｜AUI 與分層、門檻濾除

**提示詞：**
「完成 `src/metrics/aui.py`：

* 函式 `compute_country_aui(df_usage, df_pop)`：計算 share(usage)/share(pop 15-64)。
* 驗證 `TWN` 的 AUI 與官方圖表接近 **2.29**（允差±0.05，若資料切片不同則只比對方向與量級、並在測試註解說明）。
* `apply_privacy_filters(df, min_conv=15, min_users=5)`：濾除不達門檻 cell。
* `assign_tier(aui)`：依報告分層區間回傳 tier。
* 單元測試覆蓋：AUI 計算、門檻濾除、分層邊界。完成後產出 `data/processed/aui_by_country.parquet`。」

## P3｜Few-shot 合作模式分類（Automation vs Augmentation）

**提示詞**：

> 你是合作模式分類器的實作者。請依 `prompts/mode_labeler.md`：
>
> * 實作 `src/labeling/mode.py::classify_mode_llm(text)`，輸出 `primary_mode, submodes, confidence, rationale`。
> * 為 `tests/test_labelers.py` 增加 5 條範例，覆蓋 directive/iteration/validation/learning 等情境。
> * 保持 deterministic（若使用隨機，固定 seed）。完成後 `pytest -q`。

## P4｜視覺化與報告

**提示詞：**
「新增 `src/viz/figures.py`：

* `plot_top_countries_aui(df)`：複製圖 2.2 風格（顯示 N）。
* `plot_aui_vs_gdp(df)`：log-log 散點，回歸線與 R²。
* `plot_mode_stacks(df_twn)`：顯示臺灣當期合作模式。
  建立 `src/report/make_report.py` 輸出 `report/INDEX_TAIWAN.md`（摘要數字、圖表連結、方法與門檻註記）。加測試：圖檔存在且非空。」

## P4｜AUI 計算、隱私門檻、Tier

**提示詞**：

> 你是資料科學家。請在 `src/metrics/aui.py` 完成下列工作：
>
> 1. `compute_country_aui(df_usage, df_pop)`：以「使用占比 / 工作年齡人口占比」計算。
> 2. `apply_privacy_filters`：`conversations<15` 或 `unique_users<5` → 濾除。
> 3. `assign_tier`：提供可配置的門檻（保留目前預設值），回傳 tier。
> 4. 增補 `tests/test_aui.py`：加入 AUI 邊界案例與 NaN 防呆。
> 5. 若你手邊有 `TWN` 子集，可新增「驗證測試」：誤差±合理範圍（避免硬鎖常數）。
>    完成後 `pytest -q`。

## P5｜擴充（縣市層級/分群）

**提示詞：**
「在不收集個資的前提下，於上傳表單新增「**自我申報縣市**」欄位（自由輸入→正規化）；新增 `src/ingest/normalize_location.py` 做縣市正規化；在 `apply_privacy_filters` 外再加「*地理×任務*」交叉表門檻。若樣本達標，輸出 `report/TW_CITY_BREAKDOWN.md`。」

## P5｜圖表與報告

**提示詞**：

> 你是資料視覺化工程師。請在 `src/viz/figures.py`：
>
> * 完成 `plot_top_countries_aui`（顯示 N、排序、座標軸標示）。
> * 完成 `plot_aui_vs_gdp`：log-log、回歸斜率（回傳 b 值，期望接近文獻 0.69，但允差）。
> * 產出圖檔到 `figures/`。
>   在 `src/report/make_report.py`：
> * 匯入 processed 結果，輸出 `report/INDEX_TAIWAN.md`（含數字、方法、資料視窗與隱私門檻說明）。
> * 寫一段 TODO：Tier 門檻與 AUI 對齊官方報告的調整流程。
>   完成後執行 `python -m src.viz.figures` 與 `python -m src.report.make_report`。

# Claude Code 用 Few-Shot 標註模板（摘要）

**`prompts/task_labeler.md`（節選）**

* System：你是任務分類器。請將中文或英文的對話摘要歸到 **O\*NET/SOC** 的*最高層級*與（可選）*任務碼*；回傳 JSON，鍵：`top_category`, `task_code`, `confidence`, `rationale`。
* Rules：不得產生個資；只看內容，不看地理；低信心（<0.6）標記為 `unknown`。
* Few-shot：提供 8–12 條樣例（教育、科研、辦公、管理、程式開發、媒體設計…），對應報告常見分佈。

**`prompts/mode_labeler.md`（節選）**

* 定義：Automation=**Directive**（一次指令完成/少互動）（+可選 Agentic）；Augmentation=**Learning/Iteration/Validation**。回 `primary_mode`, `submodes`, `confidence`。&#x20;
* Few-shot：各類 4–6 條，涵蓋「請直接產出最終結果」vs「來回修正/檢查/學習」。
