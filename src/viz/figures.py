import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np

def plot_top_countries_aui(df_path='data/processed/aui_demo.csv'):
    df = pd.read_csv(df_path)
    df = df.sort_values('AUI', ascending=False)
    Path('figures').mkdir(exist_ok=True)
    plt.figure()
    plt.bar(df['country_code'], df['AUI'])
    plt.title('AUI by Country (Demo)')
    plt.xlabel('Country')
    plt.ylabel('AUI')
    plt.tight_layout()
    plt.savefig('figures/aui_by_country.png', dpi=160)

def plot_aui_vs_gdp(aui_df, gdp_df):
    m = pd.merge(aui_df, gdp_df, on='country_code', how='inner')
    x = np.log(m['gdp_per_capita'])
    y = np.log(m['AUI'])
    # simple linear fit
    b, a = np.polyfit(x, y, 1)
    y_hat = a + b*x
    Path('figures').mkdir(exist_ok=True)
    plt.figure()
    plt.scatter(m['gdp_per_capita'], m['AUI'])
    # regression line in log-log space (draw in original space)
    xv = np.linspace(m['gdp_per_capita'].min(), m['gdp_per_capita'].max(), 100)
    yv = np.exp(a + b*np.log(xv))
    plt.plot(xv, yv)
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel('GDP per capita (log)')
    plt.ylabel('AUI (log)')
    plt.title('AUI ~ GDP^b (Demo)')
    plt.tight_layout()
    plt.savefig('figures/aui_vs_gdp.png', dpi=160)
    return b

if __name__ == '__main__':
    plot_top_countries_aui()
