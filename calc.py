import pandas as pd
import numpy as np

def process_product_data(df):
    df = df.copy()

    # 1. 数値型変換
    df['製品サイズ'] = df['製品サイズ'].astype(str).str.strip()
    df['重量'] = pd.to_numeric(df['重量'], errors='coerce')
    df['比重'] = pd.to_numeric(df['比重'], errors='coerce')

    # 2. サイズ空欄除外
    df = df[~df['製品サイズ'].isin(['nan', 'None', ''])]

    # 3. 巾・長さ分解
    size_split = df["製品サイズ"].str.split('*', n=1, expand=True)
    df["巾"] = pd.to_numeric(size_split[0], errors='coerce')
    df["長さ"] = pd.to_numeric(size_split[1], errors='coerce')
    
    # 4. 面積
    def calculate_area(row):
        m, w, l = str(row["充填機"]), row["巾"], row["長さ"]
        if pd.isna(w) or pd.isna(l): return None
        return (w - 10) * l if "FR" in m else (w - 8) * l
    df["面積"] = df.apply(calculate_area, axis=1)

    # 5. 体積
    df["体積"] = df.apply(lambda x: x["重量"] / x["比重"] if x["比重"] > 0 else None, axis=1)

    # 6. 高さ (X列)
    def calculate_height(row):
        v, a = row["体積"], row["面積"]
        if pd.isna(v) or pd.isna(a) or a == 0: return None
        return (v / a) * 1000000 * 1.9
    df["高さ"] = df.apply(calculate_height, axis=1)

    # 7. 上限高・下限高 (各行の高さ X に対する計算)
    # Excel式: X - STDEV.P(X) - SQRT(STDEV.P(X)) + X/9
    # 単一値 X の STDEV.P は 0 なので、実質的には以下の通り
    df["上限高"] = df["高さ"] + (df["高さ"] / 9)
    df["下限高"] = df["高さ"] - (df["高さ"] / 7)
    
    return df
