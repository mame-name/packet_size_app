import pandas as pd

def process_product_data(df):
    """
    製品一覧データを整理し、製品サイズがあるものだけを抽出・分割する
    """
    df = df.copy()

    # 1. 製品サイズ列を文字列として扱い、前後の空白を除去
    df['製品サイズ'] = df['製品サイズ'].astype(str).str.strip()

    # 2. 製品サイズがブランク、NaN、Noneの行を除外
    # 文字列変換によりNaNは 'nan' になるため、それらも含めてフィルタリング
    invalid_values = ['nan', 'None', '', 'None', 'nan']
    df = df[~df['製品サイズ'].isin(invalid_values)]

    # 3. AA列（製品サイズ）を「*」で分割
    # n=1とすることで、複数の*があっても最初の1つで分割します
    size_split = df["製品サイズ"].str.split('*', n=1, expand=True)
    
    # 4. 独立した「巾」と「長さ」列を作成（分割できなかった場合は空文字）
    df["巾"] = size_split[0] if 0 in size_split.columns else ""
    df["長さ"] = size_split[1] if 1 in size_split.columns else ""
    
    return df
