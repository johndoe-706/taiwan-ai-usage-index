"""
O*NET Task Classification Module

This module provides functionality to classify conversation summaries into O*NET
occupational task categories using language models. Part of the Taiwan AI Usage Index (TAUI).
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
import pandas as pd
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaskClassifier:
    """Classifier for O*NET task categories using LLM-based classification."""

    def __init__(self, prompt_path: Optional[str] = None):
        """
        Initialize the TaskClassifier.

        Args:
            prompt_path: Path to the task labeling prompt file
        """
        self.prompt_path = prompt_path or "prompts/task_labeler.md"
        self.prompt_content = self._load_prompt()

        # O*NET task categories with skill levels
        self.categories = {
            "Computer & Mathematical": {"level": 4, "description": "Software development, data science, algorithm design"},
            "Management": {"level": 5, "description": "Executive decisions, strategic planning, team leadership"},
            "Business & Financial": {"level": 4, "description": "Financial analysis, business strategy, consulting"},
            "Life Sciences": {"level": 4, "description": "Research, medical analysis, biotechnology"},
            "Physical Sciences": {"level": 4, "description": "Engineering, research, technical analysis"},
            "Legal": {"level": 4, "description": "Legal analysis, contract review, regulatory compliance"},
            "Education": {"level": 3, "description": "Teaching, training development, curriculum design"},
            "Healthcare": {"level": 3, "description": "Medical practice, patient care, clinical analysis"},
            "Social Sciences": {"level": 3, "description": "Research, policy analysis, social services"},
            "Arts/Design/Media": {"level": 3, "description": "Creative work, design, content creation"},
            "Office/Admin": {"level": 2, "description": "Administrative tasks, data entry, scheduling"},
            "Sales": {"level": 2, "description": "Customer service, sales support, basic marketing"},
            "Production": {"level": 1, "description": "Manufacturing, assembly, quality control"},
            "Other": {"level": 1, "description": "General support tasks, maintenance, basic services"}
        }

    def _load_prompt(self) -> str:
        """Load the task classification prompt from file."""
        try:
            prompt_file = Path(self.prompt_path)
            if prompt_file.exists():
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                logger.warning(f"Prompt file not found: {self.prompt_path}")
                return self._get_default_prompt()
        except Exception as e:
            logger.error(f"Error loading prompt: {e}")
            return self._get_default_prompt()

    def _get_default_prompt(self) -> str:
        """Return a default prompt if file loading fails."""
        return """
        Classify the following conversation summary into an O*NET task category.
        Categories: Computer & Mathematical, Management, Business & Financial, etc.
        Respond with JSON containing top_category, task_code, confidence, and rationale.
        """

def classify_task_llm(text: str,
                     model: str = "mock",
                     api_key: Optional[str] = None,
                     classifier: Optional[TaskClassifier] = None) -> Dict[str, Any]:
    """
    Classify a conversation summary into O*NET task categories using LLM.

    Args:
        text: Conversation or task description text
        model: Model identifier (currently supports "mock" for testing)
        api_key: API key for the language model (not used in mock mode)
        classifier: Pre-initialized TaskClassifier instance

    Returns:
        Dictionary containing:
        - top_category: The classified O*NET category
        - task_code: Optional fine-grained code or short label
        - confidence: Confidence score (0.0-1.0)
        - rationale: Explanation of the classification

    Raises:
        ValueError: If text is empty or invalid
        RuntimeError: If classification fails
    """
    if not text or not text.strip():
        raise ValueError("Conversation text cannot be empty")

    if classifier is None:
        classifier = TaskClassifier()

    try:
        logger.info(f"Classifying task with model: {model}")

        if model == "mock":
            # Use existing regex-based classification for mock mode
            return _classify_task_regex(text, classifier)
        else:
            # Future: Implement actual LLM API calls
            raise NotImplementedError(f"Model '{model}' not yet implemented")

    except Exception as e:
        logger.error(f"Task classification failed: {e}")
        raise RuntimeError(f"Failed to classify task: {str(e)}")

def _classify_task_regex(text: str, classifier: TaskClassifier) -> Dict[str, Any]:
    """
    Regex-based classification function for testing and fallback.
    """
    # Clean and normalize input
    text_lower = text.lower().strip()

    # Define category patterns
    category_patterns = {
        "Computer & Mathematical": [
            r'程式|代碼|code|python|java|sql|api|軟體|software|資料庫|database|演算法|algorithm',
            r'debug|重構|refactor|測試|test|開發|develop|架構|architecture'
        ],
        "Education": [
            r'教學|教材|講義|考試|學習|課程|training|education|teach|lesson',
            r'學生|student|複習|review|作業|homework|評量|assessment'
        ],
        "Business & Financial": [
            r'財務|financial|會計|accounting|投資|investment|預算|budget',
            r'分析報告|analysis|營收|revenue|成本|cost|利潤|profit'
        ],
        "Life Sciences": [
            r'生物|biology|醫學|medical|藥物|drug|基因|gene|細胞|cell',
            r'研究論文|research|實驗|experiment|臨床|clinical'
        ],
        "Management": [
            r'管理|manage|專案|project|團隊|team|策略|strategy|規劃|planning',
            r'領導|leader|協調|coordinate|組織|organize'
        ],
        "Arts/Design/Media": [
            r'設計|design|藝術|art|圖片|image|影片|video|音樂|music',
            r'創作|create|視覺|visual|美術|graphic|動畫|animation'
        ],
        "Sales": [
            r'銷售|sales|行銷|marketing|客戶|customer|推廣|promotion',
            r'業務|business development|商品|product|市場|market'
        ],
        "Office/Admin": [
            r'文書|document|報告|report|整理|organize|行政|admin|秘書|secretary',
            r'郵件|email|會議|meeting|紀錄|minutes|檔案|file'
        ],
        "Legal": [
            r'法律|law|legal|合約|contract|條款|terms|規定|regulation',
            r'訴訟|litigation|智財|intellectual property|合規|compliance'
        ],
        "Healthcare": [
            r'醫療|healthcare|護理|nursing|診斷|diagnosis|治療|treatment',
            r'病患|patient|健康|health|醫院|hospital|照護|care'
        ]
    }

    # Score each category
    scores = {}
    for category, patterns in category_patterns.items():
        score = 0
        for pattern in patterns:
            if re.search(pattern, text_lower):
                score += 1
        scores[category] = score

    # Get top category
    if max(scores.values()) == 0:
        top_category = "Unknown"
        confidence = 0.0
        rationale = "No clear category patterns detected"
    else:
        top_category = max(scores, key=scores.get)
        # Calculate confidence based on pattern matches
        max_score = scores[top_category]
        confidence = min(0.95, 0.5 + (max_score * 0.15))  # Scale confidence

        # Generate rationale
        if "程式" in text_lower or "code" in text_lower:
            rationale = "Software development or programming task"
        elif "教" in text_lower or "學" in text_lower:
            rationale = "Educational or teaching content"
        elif "財務" in text_lower or "financial" in text_lower:
            rationale = "Financial analysis or business task"
        else:
            rationale = f"Matched patterns for {top_category} category"

    # Determine task code based on specific keywords
    task_code = ""
    if "重構" in text_lower or "refactor" in text_lower:
        task_code = "code_refactor"
    elif "測試" in text_lower or "test" in text_lower:
        task_code = "testing"
    elif "分析" in text_lower or "analysis" in text_lower:
        task_code = "analysis"
    elif "設計" in text_lower or "design" in text_lower:
        task_code = "design"
    elif "報告" in text_lower or "report" in text_lower:
        task_code = "reporting"
    elif "教材" in text_lower or "teaching" in text_lower:
        task_code = "teaching_materials"

    return {
        "top_category": top_category,
        "task_code": task_code,
        "confidence": round(confidence, 2),
        "rationale": rationale
    }

def classify_batch_tasks(summaries: List[str],
                        model: str = "mock",
                        api_key: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Classify multiple conversation summaries in batch.

    Args:
        summaries: List of conversation summaries to classify
        model: Model identifier
        api_key: API key for the language model

    Returns:
        List of classification results
    """
    classifier = TaskClassifier()
    results = []

    for i, summary in enumerate(summaries):
        try:
            result = classify_task_llm(summary, model, api_key, classifier)
            result["index"] = i
            results.append(result)
        except Exception as e:
            logger.error(f"Failed to classify summary {i}: {e}")
            results.append({
                "index": i,
                "top_category": "ERROR",
                "task_code": "",
                "confidence": 0.0,
                "rationale": f"Classification failed: {str(e)}"
            })

    return results

def apply_privacy_filters(classifications: List[Dict[str, Any]],
                         min_conversations: int = 15,
                         min_users: int = 5) -> List[Dict[str, Any]]:
    """
    Apply privacy filters to classification results.

    Suppresses categories with fewer than minimum thresholds for privacy protection.

    Args:
        classifications: List of classification results
        min_conversations: Minimum number of conversations required
        min_users: Minimum number of users required (mock implementation)

    Returns:
        Filtered classification results with suppressed categories marked
    """
    # Count classifications by category
    category_counts = {}
    for classification in classifications:
        category = classification.get("top_category", "Unknown")
        category_counts[category] = category_counts.get(category, 0) + 1

    # Apply suppression
    filtered_results = []
    for classification in classifications:
        category = classification.get("top_category", "Unknown")
        if category_counts.get(category, 0) < min_conversations:
            # Suppress this category
            filtered_classification = classification.copy()
            filtered_classification["top_category"] = "SUPPRESSED"
            filtered_classification["original_category"] = category
            filtered_classification["suppression_reason"] = f"Fewer than {min_conversations} conversations"
            filtered_results.append(filtered_classification)
        else:
            filtered_results.append(classification)

    return filtered_results

def get_category_statistics(classifications: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate statistics about task classifications.

    Args:
        classifications: List of classification results

    Returns:
        Dictionary containing classification statistics
    """
    total_count = len(classifications)
    if total_count == 0:
        return {"total": 0, "categories": {}, "average_confidence": 0.0}

    category_stats = {}
    confidence_scores = []

    for classification in classifications:
        category = classification.get("top_category", "Unknown")
        confidence = classification.get("confidence", 0.0)

        if category not in category_stats:
            category_stats[category] = {
                "count": 0,
                "percentage": 0.0,
                "avg_confidence": 0.0,
                "confidence_scores": []
            }

        category_stats[category]["count"] += 1
        category_stats[category]["confidence_scores"].append(confidence)
        confidence_scores.append(confidence)

    # Calculate percentages and averages
    for category in category_stats:
        stats = category_stats[category]
        stats["percentage"] = (stats["count"] / total_count) * 100
        stats["avg_confidence"] = sum(stats["confidence_scores"]) / len(stats["confidence_scores"])
        # Remove intermediate lists to clean up output
        del stats["confidence_scores"]

    return {
        "total": total_count,
        "categories": category_stats,
        "average_confidence": sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
    }

# Legacy function for backward compatibility
def classify_batch(texts: list) -> list:
    """Legacy function - use classify_batch_tasks instead."""
    return [classify_task_llm(text) for text in texts]

# Main execution for testing
if __name__ == "__main__":
    # Example usage
    test_summaries = [
        "User requested comprehensive market analysis of Taiwan's tech sector",
        "User needed help with data entry tasks and spreadsheet formatting",
        "User asked for Python code debugging and algorithm optimization",
        "User wanted creative design for marketing materials and branding"
    ]

    print("Testing O*NET Task Classification...")
    results = classify_batch_tasks(test_summaries, model="mock")

    for i, result in enumerate(results):
        print(f"\nSummary {i+1}: {test_summaries[i][:50]}...")
        print(f"Category: {result['top_category']}")
        print(f"Task Code: {result['task_code']}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Rationale: {result['rationale']}")

    print("\n" + "="*50)
    print("Classification Statistics:")
    stats = get_category_statistics(results)
    print(json.dumps(stats, indent=2))
