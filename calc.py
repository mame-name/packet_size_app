import pandas as pd
import numpy as np

def process_product_data(df):
    """
    製品一覧データを整理し、面積、体積、高さに加えて、
    統計値を用いた上限高・下限高を算出する。
    """
    df = df.copy()

    # 1. 各列を数値型に変換
    df['製品サイズ'] = df['製品サイズ'].astype(str).str.strip()
    df['重量'] = pd.to_numeric(df['重量'], errors='coerce')
    df['比重'] = pd.to_numeric(df['比重'], errors='coerce')

    # 2. 製品サイズがブランクの行を除外
    invalid_values = ['nan', 'None', '']
    df = df[~df['製品サイズ'].isin(invalid_values)]

    # 3. 製品サイズを「*」で分割し数値化
    size_split = df["製品サイズ"].str.split('*', n=1, expand=True)
    df["巾"] = pd.to_numeric(size_split[0], errors='coerce')
    df["長さ"] = pd.to_numeric(size_split[1], errors='coerce')
    
    # 4. 「面積」算出
    def calculate_area(row):
        machine_name = str(row["充填機"])
        w, l = row["巾"], row["長さ"]
        if pd.isna(w) or pd.isna(l): return None
        return (w - 10) * l if "FR" in machine_name else (w - 8) * l

    df["面積"] = df.apply(calculate_area, axis=1)

    # 5. 「体積」算出
    df["体積"] = df.apply(lambda x: x["重量"] / x["比重"] if x["比重"] > 0 else None, axis=1)

    # 6. 「高さ」算出 (X列に相当)
    def calculate_height(row):
        v, a = row["体積"], row["面積"]
        if pd.isna(v) or pd.isna(a) or a == 0: return None
        return (v / a) * 1000000 * 1.9

    df["高さ"] = df.apply(calculate_height, axis=1)

    # --- 統計値を用いた上限・下限の算出 ---
    # 有効な「高さ」のデータから全体の標準偏差(STDEV.P相当)を取得
    valid_heights = df["高さ"].dropna()
    if not valid_heights.empty:
        stdev_p = np.std(valid_heights) # 標本標準偏差ではなく母標準偏差
        
        # 上限高: X - stdev - sqrt(stdev) + X/9
        df["上限高"] = df["高さ"] - stdev_p - np.sqrt(stdev_p) + (df["高さ"] / 9)
        
        # 下限高: X - stdev - sqrt(stdev) - X/7
        df["下限高"] = df["高さ"] - stdev_p - np.sqrt(stdev_p) - (df["高さ"] / 7)
    else:
        df["上限高"] = None
        df["下限高"] = None
    
    return df
