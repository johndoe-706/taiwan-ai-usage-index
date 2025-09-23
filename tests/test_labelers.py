import pytest
from src.labeling.onets import classify_task_llm, classify_batch as classify_task_batch
from src.labeling.mode import classify_mode_llm, classify_batch as classify_mode_batch

def test_task_labeler_shape():
    out = classify_task_llm("請幫我解釋傅立葉轉換")
    assert set(out.keys()) == {'top_category','task_code','confidence','rationale'}

def test_mode_labeler_shape():
    out = classify_mode_llm("我們一段一段修改程式直到通過測試")
    assert set(out.keys()) == {'primary_mode','submodes','confidence','rationale'}

class TestTaskClassifier:
    def test_code_refactor_task(self):
        text = "幫我把這段 Python 程式重構成模組並加入單元測試"
        result = classify_task_llm(text)

        assert result["top_category"] == "Computer & Mathematical"
        assert result["task_code"] == "code_refactor"
        assert result["confidence"] >= 0.6
        assert "rationale" in result

    def test_education_task(self):
        text = "請設計高中生物的期末考複習講義與 5 題選擇題"
        result = classify_task_llm(text)

        assert result["top_category"] == "Education"
        assert result["confidence"] >= 0.5

    def test_financial_analysis(self):
        text = "撰寫財務比率分析摘要，並生成三張圖表"
        result = classify_task_llm(text)

        assert result["top_category"] == "Business & Financial"
        assert result["confidence"] >= 0.5

    def test_batch_classification(self):
        texts = [
            "寫一個排序演算法",
            "準備教學材料",
            "分析股票數據"
        ]
        results = classify_task_batch(texts)

        assert len(results) == 3
        assert results[0]["top_category"] == "Computer & Mathematical"
        assert results[1]["top_category"] == "Education"

class TestModeClassifier:
    def test_automation_directive(self):
        text = "寫出 500 字的新聞稿定稿"
        result = classify_mode_llm(text)

        assert result["primary_mode"] == "automation"
        assert "directive" in result["submodes"]
        assert result["confidence"] >= 0.5

    def test_augmentation_iteration(self):
        text = "我們一段一段修改程式直到通過測試"
        result = classify_mode_llm(text)

        assert result["primary_mode"] == "augmentation"
        assert "iteration" in result["submodes"] or "validation" in result["submodes"]
        assert result["confidence"] >= 0.5

    def test_augmentation_learning(self):
        text = "請教我 transformer 的注意力機制，並舉例"
        result = classify_mode_llm(text)

        assert result["primary_mode"] == "augmentation"
        assert "learning" in result["submodes"]
        assert result["confidence"] >= 0.5
