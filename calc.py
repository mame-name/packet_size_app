import pandas as pd
import numpy as np

def process_product_data(df):
    df = df.copy()

    # 1. 数値型変換
    df['製品サイズ'] = df['製品サイズ'].astype(str).str.strip()
    df['重量'] = pd.to_numeric(df['重量'], errors='coerce')
    df['比重'] = pd.to_numeric(df['比重'], errors='coerce')
    # シール形状を文字列としてクリーンアップ
    df['シール形状'] = df['シール形状'].astype(str).str.strip()

    # 2. サイズ空欄除外
    df = df[~df['製品サイズ'].isin(['nan', 'None', ''])]

    # 3. 巾・長さ分解
    size_split = df["製品サイズ"].str.split('*', n=1, expand=True)
    df["巾"] = pd.to_numeric(size_split[0], errors='coerce')
    df["長さ"] = pd.to_numeric(size_split[1], errors='coerce')
    
    # 4. 面積 (シール形状による分岐ロジック)
    def calculate_area(row):
        m = str(row["充填機"])
        w = row["巾"]
        l = row["長さ"]
        s = str(row["シール形状"]) # app.pyで取得したAC列(28)

        if pd.isna(w) or pd.isna(l): 
            return None
        
        # 巾の調整: FRなら-10、それ以外は-8
        adj_w = (w - 10) if "FR" in m else (w - 8)

        # シール形状による計算分岐
        if "フラット" in s:
            # フラット：巾調整 * (長さ - 15)
            area = adj_w * (l - 15)
        elif "ビン口" in s:
            # ビン口：(巾調整 * (長さ - 24)) + 40
            area = (adj_w * (l - 24)) + 40
        else:
            # どちらでもない場合は従来の単純計算（予備ロジック）
            area = adj_w * l
            
        return area

    df["面積"] = df.apply(calculate_area, axis=1)

    # 5. 体積 (mm3換算用の基礎データ)
    # 重量(g) / 比重 = 体積(cm3)
    df["体積"] = df.apply(lambda x: x["重量"] / x["比重"] if x["比重"] > 0 else None, axis=1)

    # 6. 高さ
    def calculate_height(row):
        v, a = row["体積"], row["面積"]
        if pd.isna(v) or pd.isna(a) or a <= 0: 
            return None
        # cm3からmm3へ換算(1000)し、さらに高さ係数1.9を乗じる
        return (v / a) * 1000000 * 1.9
    
    df["高さ"] = df.apply(calculate_height, axis=1)

    # 7. 上限高・下限高
    # 現場の許容範囲を示すガイドライン
    df["上限高"] = df["高さ"] + (df["高さ"] / 9)
    df["下限高"] = df["高さ"] - (df["高さ"] / 7)
    
    return df
