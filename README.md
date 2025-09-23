# Taiwan AI Usage Index (TAUI)

Reproduce key parts of the *Anthropic Economic Index* methodology for Taiwan using only local code & files (Claude Code-friendly).

## Highlights
- **AUI** (AI Usage Index): usage share / working-age population share (15–64). 
- **Privacy cell suppression**: drop any geo×segment cells with `<15` conversations **or** `<5` unique users`.
- **Labeling** (few-shot LLM via Claude Code): 
  - Task → O*NET/SOC top category.
  - Collaboration mode → automation (directive/agentic) vs augmentation (learning/iteration/validation).

## Quickstart
```bash
# 1) Create venv and install deps
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2) Run tests (TDD baseline)
pytest -q

# 3) Prepare sample pipeline run
python -m src.metrics.aui --demo

# 4) Build figures and report (with sample data)
python -m src.viz.figures
python -m src.report.make_report
```

## Data Layout
```
data/
  raw/         # do NOT commit private raw files
  interim/     # cleaned / normalized
  processed/   # aggregated / metrics
```

## Notes
- This repo is scaffolding for research reproducibility. Replace/extend sample data with your own **de-identified** volunteer data or open data slices.
- Avoid committing PII. The tests enforce privacy filtering behavior.
