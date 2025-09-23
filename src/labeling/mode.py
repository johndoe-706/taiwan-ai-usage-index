"""
Collaboration Mode Classification Module

This module provides functionality to classify conversation summaries into different
human-AI collaboration modes. Part of the Taiwan AI Usage Index (TAUI).
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

class ModeClassifier:
    """Classifier for human-AI collaboration modes using LLM-based classification."""

    def __init__(self, prompt_path: Optional[str] = None):
        """
        Initialize the ModeClassifier.

        Args:
            prompt_path: Path to the mode labeling prompt file
        """
        self.prompt_path = prompt_path or "prompts/mode_labeler.md"
        self.prompt_content = self._load_prompt()

        # Collaboration modes with descriptions
        self.modes = {
            "automation": {
                "description": "AI executes tasks with minimal human intervention",
                "submodes": ["directive", "agentic"],
                "indicators": ["single deliverable", "autonomous execution", "minimal iteration"]
            },
            "augmentation": {
                "description": "AI enhances human capabilities through collaboration",
                "submodes": ["learning", "iteration", "validation"],
                "indicators": ["explanation", "multi-turn refinement", "quality checking"]
            }
        }

    def _load_prompt(self) -> str:
        """Load the mode classification prompt from file."""
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
        Classify the following conversation summary into a collaboration mode.
        Modes: automation (directive/agentic) or augmentation (learning/iteration/validation)
        Respond with JSON containing primary_mode, submodes, confidence, and rationale.
        """

def classify_mode_llm(text: str,
                     model: str = "mock",
                     api_key: Optional[str] = None,
                     classifier: Optional[ModeClassifier] = None) -> Dict[str, Any]:
    """
    Classify a conversation summary into collaboration modes using LLM.

    Args:
        text: Conversation or task description text
        model: Model identifier (currently supports "mock" for testing)
        api_key: API key for the language model (not used in mock mode)
        classifier: Pre-initialized ModeClassifier instance

    Returns:
        Dictionary containing:
        - primary_mode: The primary collaboration mode (automation/augmentation)
        - submodes: List of applicable submodes
        - confidence: Confidence score (0.0-1.0)
        - rationale: Explanation of the classification

    Raises:
        ValueError: If text is empty or invalid
        RuntimeError: If classification fails
    """
    if not text or not text.strip():
        raise ValueError("Conversation text cannot be empty")

    if classifier is None:
        classifier = ModeClassifier()

    try:
        logger.info(f"Classifying collaboration mode with model: {model}")

        if model == "mock":
            # Use existing regex-based classification for mock mode
            return _classify_mode_regex(text, classifier)
        else:
            # Future: Implement actual LLM API calls
            raise NotImplementedError(f"Model '{model}' not yet implemented")

    except Exception as e:
        logger.error(f"Mode classification failed: {e}")
        raise RuntimeError(f"Failed to classify collaboration mode: {str(e)}")

def _classify_mode_regex(text: str, classifier: ModeClassifier) -> Dict[str, Any]:
    """
    Regex-based classification function for testing and fallback.
    """
    # Clean and normalize input
    text_lower = text.lower().strip()

    # Define mode patterns
    automation_patterns = [
        r'完成|產出|生成|generate|create|produce|寫出|write out',
        r'立即|直接|directly|一次|single|定稿|final',
        r'自動|automate|autonomous|執行|execute'
    ]

    augmentation_patterns = [
        r'教我|teach|說明|explain|學習|learning|了解|understand',
        r'修改|modify|調整|adjust|改進|improve|迭代|iterate',
        r'檢查|check|驗證|validate|測試|test|評估|evaluate'
    ]

    # Submode patterns
    directive_patterns = [r'完成|寫出|產出|complete|write|produce|定稿|final']
    agentic_patterns = [r'自動|autonomous|執行|execute|步驟|steps']
    learning_patterns = [r'教|學|teach|learn|說明|explain|了解|understand']
    iteration_patterns = [r'修改|modify|調整|adjust|改進|improve|迭代|iterate|多次|multiple']
    validation_patterns = [r'檢查|check|驗證|validate|測試|test|評估|evaluate']

    # Count pattern matches
    automation_score = sum(1 for pattern in automation_patterns if re.search(pattern, text_lower))
    augmentation_score = sum(1 for pattern in augmentation_patterns if re.search(pattern, text_lower))

    # Determine primary mode
    if automation_score > augmentation_score:
        primary_mode = "automation"
        confidence = min(0.95, 0.5 + (automation_score * 0.15))
    elif augmentation_score > automation_score:
        primary_mode = "augmentation"
        confidence = min(0.95, 0.5 + (augmentation_score * 0.15))
    else:
        # Default to augmentation if unclear
        primary_mode = "augmentation"
        confidence = 0.5

    # Determine submodes
    submodes = []
    if any(re.search(pattern, text_lower) for pattern in directive_patterns):
        submodes.append("directive")
    if any(re.search(pattern, text_lower) for pattern in agentic_patterns):
        submodes.append("agentic")
    if any(re.search(pattern, text_lower) for pattern in learning_patterns):
        submodes.append("learning")
    if any(re.search(pattern, text_lower) for pattern in iteration_patterns):
        submodes.append("iteration")
    if any(re.search(pattern, text_lower) for pattern in validation_patterns):
        submodes.append("validation")

    # If no submodes detected, add default based on primary mode
    if not submodes:
        if primary_mode == "automation":
            submodes = ["directive"]
        else:
            submodes = ["learning"]

    # Generate rationale
    if primary_mode == "automation":
        if "directive" in submodes:
            rationale = "Single deliverable with minimal iteration"
        elif "agentic" in submodes:
            rationale = "Autonomous execution with multiple steps"
        else:
            rationale = "Task completion focused"
    else:  # augmentation
        if "learning" in submodes:
            rationale = "Explanatory learning or understanding"
        elif "iteration" in submodes and "validation" in submodes:
            rationale = "Multi-turn drafting and testing"
        elif "iteration" in submodes:
            rationale = "Iterative refinement process"
        elif "validation" in submodes:
            rationale = "Checking and validation focused"
        else:
            rationale = "Collaborative augmentation"

    return {
        "primary_mode": primary_mode,
        "submodes": submodes,
        "confidence": round(confidence, 2),
        "rationale": rationale
    }

def classify_batch_modes(summaries: List[str],
                        model: str = "mock",
                        api_key: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Classify multiple conversation summaries for collaboration modes in batch.

    Args:
        summaries: List of conversation summaries to classify
        model: Model identifier
        api_key: API key for the language model

    Returns:
        List of classification results
    """
    classifier = ModeClassifier()
    results = []

    for i, summary in enumerate(summaries):
        try:
            result = classify_mode_llm(summary, model, api_key, classifier)
            result["index"] = i
            results.append(result)
        except Exception as e:
            logger.error(f"Failed to classify summary {i}: {e}")
            results.append({
                "index": i,
                "primary_mode": "ERROR",
                "submodes": [],
                "confidence": 0.0,
                "rationale": f"Classification failed: {str(e)}"
            })

    return results

def apply_privacy_filters(classifications: List[Dict[str, Any]],
                         min_conversations: int = 15,
                         min_users: int = 5) -> List[Dict[str, Any]]:
    """
    Apply privacy filters to mode classification results.

    Suppresses modes with fewer than minimum thresholds for privacy protection.

    Args:
        classifications: List of classification results
        min_conversations: Minimum number of conversations required
        min_users: Minimum number of users required (mock implementation)

    Returns:
        Filtered classification results with suppressed modes marked
    """
    # Count classifications by mode
    mode_counts = {}
    for classification in classifications:
        mode = classification.get("primary_mode", "Unknown")
        mode_counts[mode] = mode_counts.get(mode, 0) + 1

    # Apply suppression
    filtered_results = []
    for classification in classifications:
        mode = classification.get("primary_mode", "Unknown")
        if mode_counts.get(mode, 0) < min_conversations:
            # Suppress this mode
            filtered_classification = classification.copy()
            filtered_classification["primary_mode"] = "SUPPRESSED"
            filtered_classification["original_mode"] = mode
            filtered_classification["suppression_reason"] = f"Fewer than {min_conversations} conversations"
            filtered_results.append(filtered_classification)
        else:
            filtered_results.append(classification)

    return filtered_results

def get_mode_statistics(classifications: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate statistics about collaboration mode classifications.

    Args:
        classifications: List of classification results

    Returns:
        Dictionary containing classification statistics
    """
    total_count = len(classifications)
    if total_count == 0:
        return {"total": 0, "modes": {}, "average_confidence": 0.0}

    mode_stats = {}
    confidence_scores = []

    for classification in classifications:
        mode = classification.get("primary_mode", "Unknown")
        confidence = classification.get("confidence", 0.0)

        if mode not in mode_stats:
            mode_stats[mode] = {
                "count": 0,
                "percentage": 0.0,
                "avg_confidence": 0.0,
                "confidence_scores": []
            }

        mode_stats[mode]["count"] += 1
        mode_stats[mode]["confidence_scores"].append(confidence)
        confidence_scores.append(confidence)

    # Calculate percentages and averages
    for mode in mode_stats:
        stats = mode_stats[mode]
        stats["percentage"] = (stats["count"] / total_count) * 100
        stats["avg_confidence"] = sum(stats["confidence_scores"]) / len(stats["confidence_scores"])
        # Remove intermediate lists to clean up output
        del stats["confidence_scores"]

    return {
        "total": total_count,
        "modes": mode_stats,
        "average_confidence": sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
    }

def analyze_collaboration_patterns(classifications: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze patterns in collaboration modes for insights.

    Args:
        classifications: List of classification results

    Returns:
        Dictionary containing pattern analysis
    """
    stats = get_mode_statistics(classifications)

    # Identify dominant patterns
    modes = stats.get("modes", {})
    if not modes:
        return {"error": "No modes to analyze"}

    # Find most common mode
    most_common = max(modes.items(), key=lambda x: x[1]["count"])

    # Calculate collaboration complexity score
    # Higher for augmentation, lower for automation
    complexity_weights = {
        "automation": 1.0,
        "augmentation": 2.0
    }

    weighted_score = 0
    total_count = stats["total"]

    for mode, mode_stats in modes.items():
        weight = complexity_weights.get(mode, 1.0)
        proportion = mode_stats["count"] / total_count
        weighted_score += weight * proportion

    return {
        "total_conversations": total_count,
        "most_common_mode": {
            "mode": most_common[0],
            "count": most_common[1]["count"],
            "percentage": most_common[1]["percentage"]
        },
        "collaboration_complexity_score": round(weighted_score, 2),
        "average_confidence": stats["average_confidence"],
        "mode_distribution": {mode: f"{stats['percentage']:.1f}%"
                            for mode, stats in modes.items()}
    }

# Legacy function for backward compatibility
def classify_batch(texts: List[str]) -> List[Dict[str, Any]]:
    """Legacy function - use classify_batch_modes instead."""
    return [classify_mode_llm(text) for text in texts]

# Main execution for testing
if __name__ == "__main__":
    # Example usage
    test_summaries = [
        "User provided detailed specifications and reviewed each section carefully",
        "User and AI collaborated on creative brainstorming with multiple rounds of iteration",
        "User requested analysis and AI autonomously chose methodology and presented findings",
        "User asked for assistance and AI provided recommendations that enhanced decision-making"
    ]

    print("Testing Collaboration Mode Classification...")
    results = classify_batch_modes(test_summaries, model="mock")

    for i, result in enumerate(results):
        print(f"\nSummary {i+1}: {test_summaries[i][:60]}...")
        print(f"Mode: {result['primary_mode']}")
        print(f"Submodes: {result['submodes']}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Rationale: {result['rationale']}")

    print("\n" + "="*50)
    print("Mode Statistics:")
    stats = get_mode_statistics(results)
    print(json.dumps(stats, indent=2))

    print("\n" + "="*50)
    print("Collaboration Pattern Analysis:")
    patterns = analyze_collaboration_patterns(results)
    print(json.dumps(patterns, indent=2))
