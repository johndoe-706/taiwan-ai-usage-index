# 一、文件重點速讀（帶關鍵數字與可復現要素）

* 元資料
  標題：*The Anthropic Economic Index report: Uneven geographic and enterprise AI adoption*；作者 Ruth Appel、Peter McCrory、Alex Tamkin（共同第一）、另有 Miles McCain 等；發布日 **2025-09-15**。&#x20;

* 研究資料與隱私門檻
  抽樣母體：**2025-08-04 至 08-11** 的 **100 萬**筆 Claude.ai（Free+Pro）對話，單位為「對話」而非使用者；以 IP 做國家/州地理定位；排除 VPN/anycast/hosting；地理碼使用 **ISO-3166**；**<15 對話或 <5 位獨立帳號** 的 cell 會被**自動濾除**（bottom-up 群集的門檻更高：**≥500 對話與 ≥250 帳號**）。 &#x20;

* **AUI（Anthropic AI Usage Index）定義**
  針對某地理單位：
  AUI = (該地 Claude 使用占比) ÷ (該地 15-64 歲工作年齡人口占比)；**AUI>1 表示高於人口占比的使用強度**。

* **臺灣的 AUI 與樣本量（本研究最直接可用）**
  在 Top 20 圖表中，**Taiwan = AUI 2.29，N = 9.7k**（抽樣對話數）。

* **AUI 與所得的關係（用來建臺灣對照解釋）**
  跨國關聯呈 **冪次律**：AUI \~ GDP^0.69，R²=0.709；等價於「人均 GDP ↑1% ⇒ 人均 Claude 使用 ↑0.7%」。圖 2.4、對數座標、只納入樣本≥200 的國家。 &#x20;

* **合作模式（Automation vs Augmentation）時間變化**
  自 V1（2024 年末）到 V3：**Directive（偏自動化）由 27% → 39%**，第一次出現「**自動化比例 > 增強式**」。

* **任務組成的時間變化（教育、科研、程式）**
  教育任務占比：**9.3% → 11.0% → 12.7%**（2025/1、3、8 月）；生命/物理/社會科學 **6.3%→7.4%**；商務/財務 **6%→3%**；管理 **5%→3%**。 &#x20;
  程式相關：**新寫 code ↑4.5 個百分點（4.1%→8.6%）**、**debug ↓2.8 個百分點（16.1%→13.3%）**，顯示「修錯轉向創作」。

* **Claude.ai vs 企業 1P API（職類分佈）**
  API 流量有 **44%** 對應「Computer & Mathematical」，Claude.ai 為 **36%**；長尾高度集中：底部 80% 任務僅占 **12.7%（Claude.ai）/10.5%（API）**；對應 **Gini ≈ 0.82/0.84**。 &#x20;

* **高 AUI 地區更偏向「增強式合作」**（控制任務組成後觀察到）——做臺灣與同儕對照時可檢查此趨勢。

> 小結：這份報告提供你三個可直接在臺灣複製/映照的研究構件：**(1) AUI 指標與分層**、**(2) 任務分類（SOC/O\*NET）與使用變化**、**(3) 合作模式標註（Automation vs Augmentation）**，再加上**隱私門檻**與**抽樣時間窗**作為方法學邊界。

---

# 二、在臺灣複製研究：只用 Claude Code 的可執行計畫

> 目標：用 **Claude Code**（CLI/Chrome 版均可）驅動整個開發—從資料蒐集、標註、計算 AUI、到圖表與報告輸出。你不需額外雲服務；若要擴充地理解析或問卷，也以外掛腳本與開源資料為主，不硬編密鑰。

## 專案骨架與里程碑（TDD + 敏捷）

* **Repo 結構**

  ```
  taiwan-ai-usage-index/
  ├─ data/
  │  ├─ raw/            # 原始上傳/開放資料（含 Anthropic 開放資料子集；私有檔案不進版控）
  │  ├─ interim/        # 清理後（去識別）中間層
  │  └─ processed/      # 匯總、AUI 指標、繪圖輸入
  ├─ src/
  │  ├─ ingest/         # 匯入、格式驗證、去識別
  │  ├─ labeling/       # 任務(O*NET)與合作模式(自動化/增強) 標註器（LLM few-shot）
  │  ├─ metrics/        # AUI、分層、統計、門檻濾除
  │  ├─ viz/            # 複製圖2.2/2.4風格、臺灣城市/縣市地圖
  │  └─ report/         # 摘要、圖表導出（Markdown/HTML）
  ├─ tests/             # pytest（每個模組對應測試）
  ├─ prompts/           # Claude Code 用提示詞（任務標註few-shot、模式標註few-shot、代碼生成）
  ├─ CLAUDE.md          # 代理規則（工具白名單、TDD流程、產出路徑）
  └─ pyproject.toml / requirements.txt / Makefile
  ```

* **敏捷節奏（兩週一 Sprint，交付可運行增量）**

  * **P0（Day 1–2）**：倉庫與 TDD 腳手架（空實作 + 先寫測試）
  * **P1（Day 3–7）**：資料路徑打通（開放資料 + 自願者上傳管道 + 去識別）
  * **P2（Week 2）**：任務分類器 & 合作模式分類器（few-shot + 單元測試）
  * **P3（Week 3）**：AUI/分層計算、隱私門檻與抽樣視窗重現
  * **P4（Week 4）**：圖表（AUI Top/分層地圖/冪次律回歸）與報告
  * **P5（Week 5+）**：擴充：臺灣縣市層級（若有足夠樣本）；產業/學研/公部門分組

## 資料來源與「只用 Claude Code」的取得方式

1. **官方開放資料路徑（零敏感資訊）**
   報告提及提供「底層資料（task-level usage patterns）」，地理使用量僅對 Claude.ai 提供到**國家層級**。你可以：

   * 以 Claude Code 生成 `src/ingest/anthropic_open_data.py`，讀取 CSV/Parquet，**篩選國碼 `TWN`**，得到**臺灣的任務分布/合作模式估計**基線（與圖 2.2 的 AUI=2.29、N=9.7k 對齊）。
   * 若需與同儕（新加坡、澳洲、紐西蘭、南韓…）比較，直接在處理層留下國家清單（Top 20）。

2. **臺灣在地微型研究（自願者資料，上傳即去識別）**

   * 以 **Claude Code 生程式**（FastAPI/Flask 任一）建「**自願者對話上傳器**」：只收**對話文字**與**時間戳**，**不收 IP、姓名、Email**。
   * 上傳後本地立即「**去識別**」（刪人名/電話/地址/身分資訊等），寫入 `data/raw/*.jsonl`；再由 `src/ingest/clean.py` 規則化。
   * **隱私門檻**：依報告邏輯，發布任何交叉表前自動濾除 **(<15 對話 或 <5 使用者)** 的 cell；整體統計也提供**bootstrap 信賴區間**以反映小樣本不確定性。

> 以上兩路並行：A 路（開放資料）保證能跑通研究骨架；B 路（自願者）讓你把**臺灣內部分群與縣市層級**做深（樣本夠才開地圖）。

## 標註器（LLM 推斷，few-shot）

* **任務 → O\*NET/SOC**：依報告以職類/任務歸類為主；我們用 LLM few-shot + 正則後處理（允許多標，但落地時以主標為準）。
* **合作模式（Automation vs Augmentation）**：跟隨報告四分類再合併：Automation = *Directive*（一次交付、少互動）+（如你要）*Agentic*；Augmentation = *Learning / Task Iteration / Validation*。**同一對話可同時出現，主模式以最長或最後一段為準**；並回傳可信度分數。&#x20;

## 指標計算與統計

* **AUI（臺灣）**：
  `AUI_TWN = (TWN 對話占全球比) / (TWN 15-64歲人口占全球比)`；與報告一致，**驗證值期望≈ 2.29**。&#x20;
* **分層（Leading/Upper/Lower/Emerging/Minimal）**：使用報告提供的分位數區間（Leading 1.84–7.00 等）做對照；臺灣屬於 **Leading**。
* **冪次律回歸**：複製圖 2.4（log-log）：`ln(AUI) = 0.69*ln(GDP_pc) + c`，報告 R²=0.709；你可把臺灣放上去與鄰近經濟體比較。

## 視覺化（對齊論文圖型）

* **圖 A（臺灣與同儕 AUI 條狀圖）**：複製圖 2.2 風格、顯示 N。
* **圖 B（AUI vs GDP\_pc 的 log-log 散點）**：對齊圖 2.4。
* **圖 C（合作模式堆疊）**：重現 27%→39% 的 directive 對照，並用你的臺灣樣本估計**當期**比例。

# 延伸：在地洞察的兩個方向

1. **教育與科研**：你的領域（醫/工/資）可特別追蹤教育/科學任務的占比上升（如教育 **9.3%→12.7%**；生命/物理/社會科學 **6.3%→7.4%**），連結臺灣高教/公部門採用。&#x20;
2. **產業落差與冪次律**：用臺灣 vs 同儕的 log-log 散點，解讀 AUI 與產業結構、數位基礎、政策導向的關聯（對照報告對「數位基礎/產業結構/規範/信任」的解釋框架）。

# 實驗資料建議（在地複製研究）

1. **開放資料路線（安全、可跑通）**

   * 把官方釋出的 task-level 開放資料 CSV 放到 `data/raw/anthropic_open/`。
   * 跑 `python -m src.ingest.anthropic_open_data` → 取得 `data/interim/open/*.parquet`。
   * 用 `src/metrics/aui.py` 做匯總 → `data/processed/`。
   * 與 `gdp_demo.csv` 合併，先複製圖型邏輯。

2. **臺灣自願者路線（做縣市/分群）**

   * 做一個簡單的上傳表單（可由 Claude Code 生 Flask/FastAPI）：**只收文字與時間，不收 IP/姓名/Email**。
   * 上傳即去識別 → 存 `data/raw/volunteer/*.jsonl`；經 `validate.py` 正規化 → `data/interim/volunteer/*.parquet`。
   * 標註任務與模式 → 匯總 → 套 `apply_privacy_filters`。樣本夠再做縣市分布與地圖。
