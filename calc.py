import pandas as pd

def process_product_data(df):
    """
    製品一覧データを整理し、製品サイズがあるものだけを抽出し、
    充填機の種類に応じた計算列を追加する
    """
    df = df.copy()

    # 1. 製品サイズ列を文字列として扱い、前後の空白を除去
    df['製品サイズ'] = df['製品サイズ'].astype(str).str.strip()

    # 2. 製品サイズがブランク（nan, None, 空文字）の行を除外
    invalid_values = ['nan', 'None', '', 'None', 'nan']
    df = df[~df['製品サイズ'].isin(invalid_values)]

    # 3. AA列（製品サイズ）を「*」で分割し、数値に変換
    size_split = df["製品サイズ"].str.split('*', n=1, expand=True)
    df["巾"] = pd.to_numeric(size_split[0], errors='coerce')
    df["長さ"] = pd.to_numeric(size_split[1], errors='coerce')
    
    # 4. 充填機に応じた計算列の追加
    # 充填機列の値を文字列として扱い、「FR」が含まれているか判定
    # 計算式: FRありなら (巾-10)*長さ / なしなら (巾-8)*長さ
    def calculate_custom_value(row):
        machine_name = str(row["充填機"])
        w = row["巾"]
        l = row["長さ"]
        
        # 数値が取れない（NaN）場合は計算をスキップ
        if pd.isna(w) or pd.isna(l):
            return None
            
        if "FR" in machine_name:
            return (w - 10) * l
        else:
            return (w - 8) * l

    # 新規列「計算値（面積）」として追加
    df["計算値"] = df.apply(calculate_custom_value, axis=1)
    
    return df
