import pandas as pd

def process_product_data(df):
    """
    製品一覧データを整理し、製品サイズがあるものだけを抽出。
    面積、体積、高さを算出する。
    """
    df = df.copy()

    # 1. 計算のために各列を数値型に変換
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
    
    # 4. 「面積」列の追加
    # FRあり: (巾-10)*長さ / なし: (巾-8)*長さ
    def calculate_area(row):
        machine_name = str(row["充填機"])
        w = row["巾"]
        l = row["長さ"]
        if pd.isna(w) or pd.isna(l):
            return None
        
        if "FR" in machine_name:
            return (w - 10) * l
        else:
            return (w - 8) * l

    df["面積"] = df.apply(calculate_area, axis=1)

    # 5. 「体積」列の追加 (重量 / 比重)
    df["体積"] = df.apply(
        lambda x: x["重量"] / x["比重"] if x["比重"] > 0 else None, 
        axis=1
    )

    # 6. 「高さ」列の追加
    # 計算式: (体積 / 面積) * 1,000,000 * 1.9
    def calculate_height(row):
        v = row["体積"]
        a = row["面積"]
        if pd.isna(v) or pd.isna(a) or a == 0:
            return None
        
        return (v / a) * 1000000 * 1.9

    df["高さ"] = df.apply(calculate_height, axis=1)
    
    return dfmain()
