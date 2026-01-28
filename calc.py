import pandas as pd

def process_product_data(df):
    """
    製品一覧データを加工し、サイズ分割や計算を行う
    """
    # 念のためコピーを作成
    df = df.copy()

    # 1. AA列（製品サイズ）の分割処理
    # 「*」で分割し、前の値を「巾」、後ろの値を「長さ」として新規列作成
    # expand=Trueでデータフレームとして分割、n=1で最初の「*」のみで分割（安全策）
    split_data = df["製品サイズ"].astype(str).str.split('*', n=1, expand=True)
    
    # 2. 独立した列として格納
    # 数値変換できない場合はNaN（空）にする
    df["巾"] = pd.to_numeric(split_data[0], errors='coerce')
    df["長さ"] = pd.to_numeric(split_data[1], errors='coerce')
    
    # 3. 面積の計算（今後の最適化比較用）
    df["現状面積"] = df["巾"] * df["長さ"]
    
    # 4. バッチサイズ（1ショットあたりの重量）の確認用計算（例）
    # ショット数が0や空の場合はエラーになるため、1で埋める等の処理
    temp_shot = df["ショット"].replace(0, 1).fillna(1)
    df["1ショット重量"] = df["重量"] / temp_shot

    return df

def calculate_optimized_size(df, density_col="比重"):
    """
    (今後の拡張用) 重量と比重から理想の袋サイズを算出する関数
    """
    # ここに将来的な適正化ロジックを追加していく
    pass
    return df
