import pandas as pd
from pathlib import Path

PEERS = ["TWN","SGP","AUS","NZL","KOR","JPN","HKG","USA","CAN","GBR","DEU","FRA"]

def load_open_csvs(root: str) -> pd.DataFrame:
    rootp = Path(root)
    files = sorted(list(rootp.glob("*.csv")))
    if not files:
        raise FileNotFoundError(f"No CSV files in {rootp}")
    dfs = []
    for f in files:
        df = pd.read_csv(f)
        dfs.append(df)
    out = pd.concat(dfs, ignore_index=True)
    # expected columns: country_code, dt, task_text/task_id, collab_mode, count
    return out

def filter_peers(df: pd.DataFrame) -> pd.DataFrame:
    keep = df[df["country_code"].isin(PEERS)].copy()
    keep["period"] = "2025-08-04/11"
    return keep

def save_parquet(df: pd.DataFrame, out_path: str):
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out_path, index=False)

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--in_dir", default="data/raw/anthropic_open")
    ap.add_argument("--out", default="data/interim/open/claude_ai_by_country.parquet")
    args = ap.parse_args()
    df = load_open_csvs(args.in_dir)
    df = filter_peers(df)
    save_parquet(df, args.out)
    print(f"Saved {args.out}, rows={len(df)}")
