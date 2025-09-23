# 如何評估「臺灣版研究」是否達標（驗收清單）

* [ ] `pytest -q` 全綠（含 AUI 比例邏輯、門檻濾除、Labeler 介面 shape）。
* [ ] `python -m src.metrics.aui --demo` 產生 `data/processed/aui_demo.csv`。
* [ ] `python -m src.viz.figures` 產生 `figures/*.png`；回歸斜率 `b` 有合理數值。
* [ ] `python -m src.report.make_report` 產生 `report/INDEX_TAIWAN.md`，內含：方法、數字、資料視窗與隱私門檻。
* [ ] 以你拿到的 `TWN` 子集，跑出 **AUI≈2.29（允差）/ N≈9.7k（若資料片段一致）** 的對齊討論（可在報告寫「與官方差異來源」）。
* [ ] **AUI 計算**：以官方開放資料的 `TWN` 子集，產生 **AUI ≈ 2.29**（允差範圍內）；並列出 **N≈9.7k**（樣本大小）。
* [ ] **門檻濾除**：任何「地理×任務」表格皆保證 `<15 對話或 <5 使用者` 被壓抑。
* [ ] **合作模式**：回報臺灣*當期* directive/augmentation 佔比，並對照 V1→V3 的 **27%→39%** 變化作討論。
* [ ] **對照圖**：完成 AUI 條圖（含 N）、log-log AUI\~GDP 散點（顯示冪次律 0.69 參考線），與任務分佈圖。
* [ ] **報告**：`report/INDEX_TAIWAN.md` 附方法、門檻、視窗日期 **2025-08-04/11**。
