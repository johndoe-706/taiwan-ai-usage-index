"""
Comprehensive test suite for TAUI labeling modules.

Tests both O*NET task classification and collaboration mode classification
following TDD principles with extensive coverage.
"""

import pytest
import json
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from labeling.onets import (
    TaskClassifier,
    classify_task_llm,
    classify_batch_tasks,
    apply_privacy_filters as apply_task_privacy_filters,
    get_category_statistics
)
from labeling.mode import (
    ModeClassifier,
    classify_mode_llm,
    classify_batch_modes,
    apply_privacy_filters as apply_mode_privacy_filters,
    get_mode_statistics,
    analyze_collaboration_patterns
)

# Legacy imports for backward compatibility
from labeling.onets import classify_batch as classify_task_batch
from labeling.mode import classify_batch as classify_mode_batch

class TestTaskClassifier:
    """Test suite for O*NET task classification."""

    def test_task_classifier_initialization(self):
        """Test TaskClassifier initialization."""
        classifier = TaskClassifier()
        assert classifier is not None
        assert hasattr(classifier, 'categories')
        assert hasattr(classifier, 'prompt_content')
        assert len(classifier.categories) > 0

    def test_task_classifier_categories(self):
        """Test that TaskClassifier has expected categories."""
        classifier = TaskClassifier()
        expected_categories = [
            "Computer & Mathematical", "Management", "Business & Financial",
            "Life Sciences", "Physical Sciences", "Legal", "Education",
            "Healthcare", "Social Sciences", "Arts/Design/Media",
            "Office/Admin", "Sales", "Production", "Other"
        ]

        for category in expected_categories:
            assert category in classifier.categories
            assert "level" in classifier.categories[category]
            assert "description" in classifier.categories[category]

    def test_task_labeler_shape(self):
        """Test basic output structure."""
        out = classify_task_llm("請幫我解釋傅立葉轉換")
        assert set(out.keys()) == {'top_category','task_code','confidence','rationale'}

    def test_classify_task_llm_basic(self):
        """Test basic task classification functionality."""
        summary = "User requested comprehensive market analysis of Taiwan's tech sector"
        result = classify_task_llm(summary, model="mock")

        assert "top_category" in result
        assert "task_code" in result
        assert "confidence" in result
        assert "rationale" in result
        assert isinstance(result["confidence"], (int, float))
        assert 0.0 <= result["confidence"] <= 1.0

    def test_classify_task_llm_empty_input(self):
        """Test error handling for empty input."""
        with pytest.raises(ValueError, match="Conversation text cannot be empty"):
            classify_task_llm("")

        with pytest.raises(ValueError, match="Conversation text cannot be empty"):
            classify_task_llm("   ")

    def test_classify_task_llm_invalid_model(self):
        """Test error handling for invalid model."""
        with pytest.raises(RuntimeError, match="Failed to classify task"):
            classify_task_llm("test summary", model="invalid_model")

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
        results = classify_batch_tasks(texts)

        assert len(results) == 3
        assert results[0]["top_category"] == "Computer & Mathematical"
        assert results[1]["top_category"] == "Education"

    def test_apply_task_privacy_filters(self):
        """Test privacy filtering for task classifications."""
        classifications = [
            {"top_category": "Computer & Mathematical", "confidence": 0.9},
            {"top_category": "Computer & Mathematical", "confidence": 0.8},
            {"top_category": "Rare Category", "confidence": 0.7},  # Only 1 instance
            {"top_category": "Education", "confidence": 0.85}
        ]

        filtered = apply_task_privacy_filters(classifications, min_conversations=2)

        # Categories with only 1 instance should be suppressed
        suppressed_count = sum(1 for c in filtered if c["top_category"] == "SUPPRESSED")
        assert suppressed_count >= 1  # At least "Rare Category" and "Education" should be suppressed

        # Check that suppressed item has original category preserved
        suppressed_items = [c for c in filtered if c["top_category"] == "SUPPRESSED"]
        assert len(suppressed_items) >= 1
        suppressed_item = suppressed_items[0]
        assert "original_category" in suppressed_item
        assert "suppression_reason" in suppressed_item

    def test_get_category_statistics(self):
        """Test generation of category statistics."""
        classifications = [
            {"top_category": "Computer & Mathematical", "confidence": 0.9},
            {"top_category": "Computer & Mathematical", "confidence": 0.8},
            {"top_category": "Education", "confidence": 0.85},
            {"top_category": "Office/Admin", "confidence": 0.7}
        ]

        stats = get_category_statistics(classifications)

        assert stats["total"] == 4
        assert "categories" in stats
        assert "average_confidence" in stats

        # Check Computer & Mathematical stats
        comp_stats = stats["categories"]["Computer & Mathematical"]
        assert comp_stats["count"] == 2
        assert comp_stats["percentage"] == 50.0
        assert abs(comp_stats["avg_confidence"] - 0.85) < 0.001  # (0.9 + 0.8) / 2

    def test_get_category_statistics_empty(self):
        """Test statistics generation with empty input."""
        stats = get_category_statistics([])
        assert stats["total"] == 0
        assert stats["categories"] == {}
        assert stats["average_confidence"] == 0.0

class TestModeClassifier:
    """Test suite for collaboration mode classification."""

    def test_mode_classifier_initialization(self):
        """Test ModeClassifier initialization."""
        classifier = ModeClassifier()
        assert classifier is not None
        assert hasattr(classifier, 'modes')
        assert hasattr(classifier, 'prompt_content')
        assert len(classifier.modes) == 2

    def test_mode_classifier_modes(self):
        """Test that ModeClassifier has expected modes."""
        classifier = ModeClassifier()
        expected_modes = ["automation", "augmentation"]

        for mode in expected_modes:
            assert mode in classifier.modes
            assert "description" in classifier.modes[mode]
            assert "submodes" in classifier.modes[mode]
            assert "indicators" in classifier.modes[mode]

    def test_mode_labeler_shape(self):
        """Test basic output structure."""
        out = classify_mode_llm("我們一段一段修改程式直到通過測試")
        assert set(out.keys()) == {'primary_mode','submodes','confidence','rationale'}

    def test_classify_mode_llm_basic(self):
        """Test basic mode classification functionality."""
        summary = "User provided detailed specifications and reviewed each section"
        result = classify_mode_llm(summary, model="mock")

        assert "primary_mode" in result
        assert "submodes" in result
        assert "confidence" in result
        assert "rationale" in result
        assert 0.0 <= result["confidence"] <= 1.0

    def test_classify_mode_llm_empty_input(self):
        """Test error handling for empty input."""
        with pytest.raises(ValueError, match="Conversation text cannot be empty"):
            classify_mode_llm("")

        with pytest.raises(ValueError, match="Conversation text cannot be empty"):
            classify_mode_llm("   ")

    def test_classify_mode_llm_invalid_model(self):
        """Test error handling for invalid model."""
        with pytest.raises(RuntimeError, match="Failed to classify collaboration mode"):
            classify_mode_llm("test summary", model="invalid_model")

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

    def test_classify_batch_modes(self):
        """Test batch classification of collaboration modes."""
        summaries = [
            "User provided step-by-step instructions",
            "User and AI worked together iteratively",
            "AI handled most of the work autonomously"
        ]

        results = classify_batch_modes(summaries, model="mock")

        assert len(results) == len(summaries)
        for i, result in enumerate(results):
            assert result["index"] == i
            assert "primary_mode" in result
            assert "confidence" in result
            assert "submodes" in result

    def test_apply_mode_privacy_filters(self):
        """Test privacy filtering for mode classifications."""
        classifications = [
            {"primary_mode": "automation", "confidence": 0.9},
            {"primary_mode": "automation", "confidence": 0.8},
            {"primary_mode": "rare_mode", "confidence": 0.7},  # Only 1 instance
            {"primary_mode": "augmentation", "confidence": 0.85}
        ]

        filtered = apply_mode_privacy_filters(classifications, min_conversations=2)

        # Modes with only 1 instance should be suppressed
        suppressed_count = sum(1 for c in filtered if c["primary_mode"] == "SUPPRESSED")
        assert suppressed_count >= 1  # At least "rare_mode" and "augmentation" should be suppressed

        # Check that suppressed item has original mode preserved
        suppressed_items = [c for c in filtered if c["primary_mode"] == "SUPPRESSED"]
        assert len(suppressed_items) >= 1
        suppressed_item = suppressed_items[0]
        assert "original_mode" in suppressed_item
        assert "suppression_reason" in suppressed_item

    def test_get_mode_statistics(self):
        """Test generation of mode statistics."""
        classifications = [
            {"primary_mode": "automation", "confidence": 0.9},
            {"primary_mode": "automation", "confidence": 0.8},
            {"primary_mode": "augmentation", "confidence": 0.85},
            {"primary_mode": "augmentation", "confidence": 0.7}
        ]

        stats = get_mode_statistics(classifications)

        assert stats["total"] == 4
        assert "modes" in stats
        assert "average_confidence" in stats

        # Check automation stats
        auto_stats = stats["modes"]["automation"]
        assert auto_stats["count"] == 2
        assert auto_stats["percentage"] == 50.0
        assert abs(auto_stats["avg_confidence"] - 0.85) < 0.001  # (0.9 + 0.8) / 2

    def test_analyze_collaboration_patterns(self):
        """Test collaboration pattern analysis."""
        classifications = [
            {"primary_mode": "automation", "confidence": 0.9},
            {"primary_mode": "automation", "confidence": 0.8},
            {"primary_mode": "augmentation", "confidence": 0.85},
            {"primary_mode": "augmentation", "confidence": 0.7}
        ]

        patterns = analyze_collaboration_patterns(classifications)

        assert "total_conversations" in patterns
        assert "most_common_mode" in patterns
        assert "collaboration_complexity_score" in patterns
        assert "average_confidence" in patterns
        assert "mode_distribution" in patterns

        assert patterns["total_conversations"] == 4
        assert isinstance(patterns["collaboration_complexity_score"], (int, float))

class TestIntegration:
    """Integration tests for both labeling modules."""

    def test_full_pipeline_task_classification(self):
        """Test complete task classification pipeline."""
        summaries = [
            "User requested comprehensive market research analysis with strategic recommendations",
            "User needed help with Python debugging and code optimization for ML pipeline",
            "User asked for creative design assistance for marketing campaign materials",
            "User wanted help with basic data entry and spreadsheet organization tasks"
        ]

        # Classify tasks
        task_results = classify_batch_tasks(summaries, model="mock")

        # Apply privacy filters (should not suppress anything with 4 items)
        filtered_tasks = apply_task_privacy_filters(task_results, min_conversations=2)

        # Generate statistics
        task_stats = get_category_statistics(filtered_tasks)

        # Verify pipeline completed successfully
        assert len(task_results) == 4
        assert len(filtered_tasks) == 4
        assert task_stats["total"] == 4
        assert len(task_stats["categories"]) > 0

    def test_full_pipeline_mode_classification(self):
        """Test complete mode classification pipeline."""
        summaries = [
            "User provided detailed specifications and reviewed each implementation step",
            "User and AI collaborated on creative brainstorming with iterative refinement",
            "User delegated analysis task and AI autonomously chose methodology",
            "User requested assistance and AI provided helpful recommendations and insights"
        ]

        # Classify modes
        mode_results = classify_batch_modes(summaries, model="mock")

        # Apply privacy filters
        filtered_modes = apply_mode_privacy_filters(mode_results, min_conversations=1)

        # Generate statistics and patterns
        mode_stats = get_mode_statistics(filtered_modes)
        patterns = analyze_collaboration_patterns(filtered_modes)

        # Verify pipeline completed successfully
        assert len(mode_results) == 4
        assert len(filtered_modes) == 4
        assert mode_stats["total"] == 4
        assert patterns["total_conversations"] == 4

    def test_error_resilience(self):
        """Test system resilience to various error conditions."""
        # Test with mixed valid and invalid inputs
        mixed_summaries = [
            "Valid task summary for analysis",
            "",  # Empty string
            "Another valid summary"
        ]

        # Test task classification
        task_results = classify_batch_tasks(mixed_summaries, model="mock")

        # Should have results for valid summaries and error entries for invalid ones
        assert len(task_results) == 3

        # At least one should be an error (the empty string)
        error_count = sum(1 for r in task_results if r["top_category"] == "ERROR")
        assert error_count >= 1

        # Test mode classification
        mode_results = classify_batch_modes(mixed_summaries, model="mock")
        assert len(mode_results) == 3

        error_count = sum(1 for r in mode_results if r["primary_mode"] == "ERROR")
        assert error_count >= 1

if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
