from typing import Dict, Any
import json
import re

def classify_task_llm(text: str) -> Dict[str, Any]:
    """LLM-based classifier for O*NET/SOC task categorization.

    Args:
        text: Conversation or task description text

    Returns:
        Dict with top_category, task_code, confidence, and rationale
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

def classify_batch(texts: list) -> list:
    """Classify multiple texts in batch."""
    return [classify_task_llm(text) for text in texts]
