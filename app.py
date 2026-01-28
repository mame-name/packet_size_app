import streamlit as st
import pandas as pd
from calc import process_product_data  # calcから関数を呼び出す

def main():
    st.title("小袋サイズ適正化アプリ")
    
    uploaded_file = st.file_uploader("実績XLSMをアップロード", type=['xlsm'])
    
    if uploaded_file:
        # 読み込み（インデックスで列を指定）
        target_indices = [0, 1, 5, 6, 9, 15, 17, 18, 25, 26]
        col_names = ["製品コード", "名前", "重量", "入数", "比重", "外装", "顧客名", "ショット", "粘度", "製品サイズ"]
        
        df_raw = pd.read_excel(
            uploaded_file, 
            sheet_name="製品一覧", 
            usecols=target_indices, 
            names=col_names, # 読み込み時に名前をつけて独立させる
            engine='openpyxl'
        )
        
        # calc側の関数を呼び出して「分割・加工」を実行
        df_final = process_product_data(df_raw)
        
        st.write("### 処理結果データ")
        st.dataframe(df_final)

if __name__ == "__main__":
    main()
