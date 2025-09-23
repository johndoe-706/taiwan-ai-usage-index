from typing import Dict, Any, List
import re

def classify_mode_llm(text: str) -> Dict[str, Any]:
    """Classify collaboration mode for a conversation.

    Args:
        text: Conversation or task description text

    Returns:
        Dict with primary_mode, submodes, confidence, and rationale
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

def classify_batch(texts: List[str]) -> List[Dict[str, Any]]:
    """Classify multiple texts in batch."""
    return [classify_mode_llm(text) for text in texts]
