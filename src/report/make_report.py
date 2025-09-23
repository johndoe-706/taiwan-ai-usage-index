from pathlib import Path
import pandas as pd

def make_report():
    Path('report').mkdir(exist_ok=True)
    p = Path('report/INDEX_TAIWAN.md')
    demo = Path('data/processed/aui_demo.csv')
    if demo.exists():
        df = pd.read_csv(demo)
        twn = df[df['country_code']=='TWN'].copy()
        txt = f"""# Taiwan AI Usage Index — Demo Report

- Data window: 2025-08-04/11 (illustrative)
- AUI (demo): {float(twn['AUI'].iloc[0]):.2f} (tier: {twn['tier'].iloc[0]})
- Figures: see `figures/`

> Replace demo data with real, de-identified inputs and re-run pipeline.
"""
    else:
        txt = """# Taiwan AI Usage Index — Report

No data found. Run the pipeline to generate processed metrics.
"""
    p.write_text(txt, encoding='utf-8')
    print(f"Wrote {p}")

if __name__ == '__main__':
    make_report()
