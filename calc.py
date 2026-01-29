import pandas as pd
import numpy as np

def process_product_data(df):
    df = df.copy()

    # 1. 数値型変換
    df['製品サイズ'] = df['製品サイズ'].astype(str).str.strip()
    df['重量'] = pd.to_numeric(df['重量'], errors='coerce')
    df['比重'] = pd.to_numeric(df['比重'], errors='coerce')
    # 「シール形状」から「シール」に名称統一して読み込み
    df['シール'] = df['シール形状'].astype(str).str.strip()

    # 2. サイズ空欄除外
    df = df[~df['製品サイズ'].isin(['nan', 'None', ''])]

    # 3. 巾・長さ分解
    size_split = df["製品サイズ"].str.split('*', n=1, expand=True)
    df["巾"] = pd.to_numeric(size_split[0], errors='coerce')
    df["長さ"] = pd.to_numeric(size_split[1], errors='coerce')
    
    # 4. 面積 (シールの種類による分岐)
    def calculate_area(row):
        m = str(row["充填機"])
        w = row["巾"]
        l = row["長さ"]
        s = str(row["シール"]) # 「フラット」か「ビン口」か

        if pd.isna(w) or pd.isna(l): return None
        
        # 巾の調整
        adj_w = (w - 10) if "FR" in m else (w - 8)

        # 面積計算ロジック
        if "フラット" in s:
            area = adj_w * (l - 15)
        elif "ビン口" in s:
            area = (adj_w * (l - 24)) + 40
        else:
            # 判別できない場合は基本計算
            area = adj_w * l
            
        return area

    df["面積"] = df.apply(calculate_area, axis=1)

    # 5. 体積
    df["体積"] = df.apply(lambda x: x["重量"] / x["比重"] if x["比重"] > 0 else None, axis=1)

    # 6. 高さ
    def calculate_height(row):
        v, a = row["体積"], row["面積"]
        if pd.isna(v) or pd.isna(a) or a <= 0: return None
        return (v / a) * 1000000 * 1.9
    
    df["高さ"] = df.apply(calculate_height, axis=1)

    # 7. 上限高・下限高
    df["上限高"] = df["高さ"] + (df["高さ"] / 9)
    df["下限高"] = df["高さ"] - (df["高さ"] / 7)
    
    return df
