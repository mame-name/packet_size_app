import pandas as pd

def process_product_data(df):
    """
    製品一覧データを整理し、サイズ列を分割する（計算は行わない）
    """
    df = df.copy()

    # AA列（製品サイズ）を「*」の前後で分割
    # 文字列として処理し、分割した1番目を「巾」、2番目を「長さ」に格納
    size_split = df["製品サイズ"].astype(str).str.split('*', n=1, expand=True)
    
    # 新規列の作成（データが存在する場合のみ格納）
    df["巾"] = size_split[0] if 0 in size_split.columns else ""
    df["長さ"] = size_split[1] if 1 in size_split.columns else ""
    
    # その他の列（重量、比重、ショット等）は読み込んだ状態のまま保持されます
    return df
