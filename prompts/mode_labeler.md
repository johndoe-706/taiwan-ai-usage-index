# Collaboration Mode Classification

## Instructions
You are an expert AI researcher specializing in human-AI collaboration patterns. Your task is to classify conversation summaries based on the collaboration mode between humans and AI systems.

## Classification Framework

### Primary Modes

#### Automation
- **Directive**: Human provides clear specifications, AI executes with minimal back-and-forth
- **Agentic**: AI operates with high autonomy, making decisions and executing multi-step processes

#### Augmentation
- **Learning**: AI explains concepts, teaches, or helps humans understand complex topics
- **Iteration**: Multi-turn collaborative refinement, drafting, and improvement processes
- **Validation**: AI assists with checking, testing, evaluating, and quality assurance

## Output Format
Respond with JSON containing:
- `primary_mode`: "automation" or "augmentation"
- `submodes`: Array of applicable submodes ["directive", "agentic", "learning", "iteration", "validation"]
- `confidence`: Confidence score (0.0-1.0)
- `rationale`: Brief explanation (one or two sentences)

## Classification Guidelines

### Automation Indicators
- Single-turn requests for deliverables
- Clear specifications with minimal iteration
- Task completion focus
- Human delegates, AI executes
- Minimal collaborative refinement

### Augmentation Indicators
- Multi-turn conversations
- Learning and explanation requests
- Iterative improvement processes
- Human-AI collaborative problem-solving
- Validation and quality checking

## Few-Shot Examples

### Example 1: Automation - Directive
**Input**: "寫出 500 字的新聞稿定稿"
**Output**: {"primary_mode": "automation", "submodes": ["directive"], "confidence": 0.78, "rationale": "Single deliverable request with minimal iteration expected"}

### Example 2: Augmentation - Iteration + Validation
**Input**: "我們一段一段修改程式直到通過測試"
**Output**: {"primary_mode": "augmentation", "submodes": ["iteration", "validation"], "confidence": 0.83, "rationale": "Multi-turn drafting and testing process with collaborative refinement"}

### Example 3: Augmentation - Learning
**Input**: "請教我 transformer 的注意力機制，並舉例"
**Output**: {"primary_mode": "augmentation", "submodes": ["learning"], "confidence": 0.81, "rationale": "Explanatory learning focused on understanding complex concepts"}

### Example 4: Automation - Agentic
**Input**: "Analyze Taiwan's AI policy landscape and create comprehensive report with recommendations"
**Output**: {"primary_mode": "automation", "submodes": ["agentic"], "confidence": 0.79, "rationale": "Autonomous multi-step analysis and report generation"}

### Example 5: Augmentation - Iteration
**Input**: "Let's refine this marketing strategy through multiple rounds of feedback"
**Output**: {"primary_mode": "augmentation", "submodes": ["iteration"], "confidence": 0.84, "rationale": "Collaborative iterative improvement process"}

### Example 6: Augmentation - Validation
**Input**: "Check my financial model calculations and identify potential errors"
**Output**: {"primary_mode": "augmentation", "submodes": ["validation"], "confidence": 0.80, "rationale": "Quality assurance and error checking focus"}

## Special Considerations
- **Mixed modes**: If multiple patterns appear, classify based on dominant interaction style
- **Evolving patterns**: Consider the overall conversation arc, not just individual exchanges
- **Context dependency**: Same task type can have different modes based on execution approach
- **Cultural factors**: Account for different communication styles in zh-TW vs en-US contexts

## Privacy Protection
Apply cell suppression: If fewer than 15 conversations or 5 users in any mode category, mark as "SUPPRESSED" for privacy protection.

## Quality Indicators
- High confidence (>0.8): Clear patterns with strong indicators
- Medium confidence (0.6-0.8): Recognizable patterns with some ambiguity
- Low confidence (<0.6): Mixed or unclear patterns, consider "Unknown" classification
