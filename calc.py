import pandas as pd

def process_product_data(df):
    """
    取り込んだデータフレームを整理・分割するロジック
    """
    # 1. 必要な列の抽出とリネーム（app側で読み込んだ後のdfを想定）
    # ※列のインデックス指定は読み込み時にapp側で行うのが一般的ですが、
    # ここでは「独立した列」として扱う処理をまとめます。
    
    # 2. AA列（製品サイズ）の分割
    # 「*」で分割し、前の値を「巾」、後ろの値を「長さ」として新規列作成
    # str.splitの結果を数値型(float)に変換
    size_split = df["製品サイズ"].astype(str).str.split('*', expand=True)
    
    if size_split.shape[1] >= 2:
        df["巾"] = pd.to_numeric(size_split[0], errors='coerce')
        df["長さ"] = pd.to_numeric(size_split[1], errors='coerce')
    else:
        df["巾"] = None
        df["長さ"] = None
        
    # 3. 今後の計算に使う「面積」などもここで作っておくと便利
    df["現状面積"] = df["巾"] * df["長さ"]
    
    return df}
