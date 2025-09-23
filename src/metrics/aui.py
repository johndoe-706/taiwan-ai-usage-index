import pandas as pd
import numpy as np
from dataclasses import dataclass
from pathlib import Path

@dataclass
class TierThresholds:
    # Default bins are configurable; tune to match report bins.
    minimal: float = 0.50
    emerging: float = 0.90
    lower: float = 1.10
    upper: float = 1.84
    leading: float = 7.00

def compute_share(series: pd.Series) -> pd.Series:
    total = series.sum()
    if total == 0:
        return series.copy() * np.nan
    return series / total

def compute_country_aui(df_usage: pd.DataFrame, df_pop: pd.DataFrame) -> pd.DataFrame:
    """Compute AUI by country: usage_share / pop_share (15–64).
    df_usage: columns ['country_code','conversations']
    df_pop:   columns ['country_code','working_age_pop']
    """
    u = df_usage.groupby('country_code', as_index=False)['conversations'].sum()
    u['usage_share'] = compute_share(u['conversations'])
    p = df_pop.groupby('country_code', as_index=False)['working_age_pop'].sum()
    p['pop_share'] = compute_share(p['working_age_pop'])
    m = pd.merge(u, p, on='country_code', how='inner')
    m['AUI'] = m['usage_share'] / m['pop_share']
    return m

def apply_privacy_filters(df: pd.DataFrame, min_conv: int = 15, min_users: int = 5) -> pd.DataFrame:
    cols = df.columns
    need_cols = []
    if 'conversations' in cols: need_cols.append('conversations')
    if 'unique_users' in cols: need_cols.append('unique_users')
    if not need_cols:
        return df.copy()
    ok = pd.Series(True, index=df.index)
    if 'conversations' in cols:
        ok &= df['conversations'].fillna(0) >= min_conv
    if 'unique_users' in cols:
        ok &= df['unique_users'].fillna(0) >= min_users
    return df[ok].copy()

def assign_tier(aui: float, th: TierThresholds = TierThresholds()) -> str:
    if np.isnan(aui):
        return 'unknown'
    if aui < th.minimal:
        return 'below-min'
    if aui < th.emerging:
        return 'emerging'
    if aui < th.lower:
        return 'lower'
    if aui < th.upper:
        return 'upper'
    if aui <= th.leading:
        return 'leading'
    return 'outlier'

def _demo():
    # Tiny demo data
    df_usage = pd.DataFrame({
        'country_code': ['TWN','USA','JPN'],
        'conversations': [9700, 300000, 150000]
    })
    df_pop = pd.DataFrame({
        'country_code': ['TWN','USA','JPN'],
        'working_age_pop': [17000000, 210000000, 74000000]  # illustrative only
    })
    out = compute_country_aui(df_usage, df_pop)
    out['tier'] = out['AUI'].apply(assign_tier)
    Path('data/processed').mkdir(parents=True, exist_ok=True)
    out.to_csv('data/processed/aui_demo.csv', index=False)
    print(out)

if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--demo', action='store_true', help='run small demo and write data/processed/aui_demo.csv')
    args = ap.parse_args()
    if args.demo:
        _demo()
