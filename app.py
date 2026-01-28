import pandas as pd
import streamlit as st

def load_xlsm_data(file):
    try:
        # xlsmファイルを読み込み（engine='openpyxl'が必要）
        # data_only=Trueにしたい場合は、内部でopenpyxlを直接呼ぶ必要がありますが、
        # pandas経由でも通常の値は取得可能です。
        df = pd.read_excel(file, engine='openpyxl', sheet_name=0) # 最初のシート
        return df
    except Exception as e:
        st.error(f"読み込みエラー: {e}")
        return None

# App部分の修正
uploaded_file = st.file_uploader("実績XLSMをアップロード", type=['xlsm'])
if uploaded_file:
    df = load_xlsm_data(uploaded_file)
    if df is not None:
        st.success("データの取り込みに成功しました！")
        # ここから先のバッチサイズ計算へ渡す
