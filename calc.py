import pandas as pd

def process_product_data(df):
    """
    製品一覧データを加工し、サイズ分割を行う（計算はしない）
    """
    df = df.copy()

    # 1. AA列（製品サイズ）を「*」で分割
    # 数値変換もせず、まずは文字列のまま「巾」と「長さ」に分けます
    size_split = df["製品サイズ"].astype(str).str.split('*', n=1, expand=True)
    
    # 2. 新規列として格納
    # 分割できなかった場合を考慮し、列が存在するか確認して代入
    df["巾"] = size_split[0] if 0 in size_split.columns else None
    df["長さ"] = size_split[1] if 1 in size_split.columns else None
    
    # この時点では「重量」「ショット」「比重」なども
    # エクセルに入っている状態のまま各列に保持されています。

    return df
