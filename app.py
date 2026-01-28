import streamlit as st
import pandas as pd
from calc import process_product_data

st.set_page_config(layout="wide")

def main():
    st.title("📦 製品データ抽出ツール")

    uploaded_file = st.file_uploader("実績XLSM（製品一覧シート）を選択", type=['xlsm'])
    
    if uploaded_file:
        try:
            # 指定された列インデックス
            target_indices = [0, 1, 5, 6, 9, 15, 17, 18, 25, 26]
            col_names = [
                "製品コード", "名前", "重量", "入数", "比重", 
                "外装", "顧客名", "ショット", "粘度", "製品サイズ"
            ]
            
            # データ読み込み（型を指定せずそのまま取り込む）
            df_raw = pd.read_excel(
                uploaded_file, 
                sheet_name="製品一覧", 
                usecols=target_indices, 
                names=col_names,
                engine='openpyxl',
                dtype=object # すべて一旦オブジェクト型としてそのまま取り込む
            )
            
            # 分割ロジックのみ実行
            df_final = process_product_data(df_raw)
            
            st.success("指定列の抽出とサイズ分割が完了しました。")
            st.dataframe(df_final, use_container_width=True)

        except Exception as e:
            st.error(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    main()main()
