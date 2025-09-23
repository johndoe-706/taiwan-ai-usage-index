import pandas as pd
from src.metrics.aui import compute_country_aui, assign_tier, TierThresholds, apply_privacy_filters

def test_aui_basic_ratio():
    usage = pd.DataFrame({'country_code':['A','B'], 'conversations':[50,50]})
    pop = pd.DataFrame({'country_code':['A','B'], 'working_age_pop':[1,9]})
    out = compute_country_aui(usage, pop).set_index('country_code')
    # Usage shares are 0.5/0.5, pop shares are 0.1/0.9 -> AUI are 5.0 and 0.555...
    assert abs(out.loc['A','AUI'] - 5.0) < 1e-6
    assert abs(out.loc['B','AUI'] - (0.5/0.9)) < 1e-6

def test_privacy_filters():
    df = pd.DataFrame({
        'geo':['X','Y','Z'],
        'conversations':[14, 15, 100],
        'unique_users':[10, 4, 50]
    })
    out = apply_privacy_filters(df, min_conv=15, min_users=5)
    # 'X': conv<15 -> drop; 'Y': users<5 -> drop; 'Z': keep
    assert list(out['geo']) == ['Z']

def test_tiers_ordering():
    th = TierThresholds(minimal=0.5, emerging=0.9, lower=1.1, upper=1.84, leading=7.0)
    assert assign_tier(0.3, th) == 'below-min'
    assert assign_tier(0.7, th) == 'emerging'
    assert assign_tier(1.05, th) == 'lower'
    assert assign_tier(1.7, th) == 'upper'
    assert assign_tier(2.0, th) == 'leading'
