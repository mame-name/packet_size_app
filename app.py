import streamlit as st
import pandas as pd
from calc import process_product_data

# 画面を広く使う
st.set_page_config(layout="wide", page_title="製品データ抽出アプリ")

def main():
    st.title("📦 製品リスト抽出・分割ツール")
    st.info("製品一覧シートから指定の10列を抽出し、サイズを『巾』と『長さ』に分割します。")

    uploaded_file = st.file_uploader("実績XLSMをアップロード", type=['xlsm'])
    
    if uploaded_file:
        try:
            # 抽出対象列のインデックス（A=0, B=1, F=5, G=6, J=9, P=15, R=17, S=18, Z=25, AA=26）
            target_indices = [0, 1, 5, 6, 9, 15, 17, 18, 25, 26]
            
            # 列名の定義（独立した列として管理）
            col_names = [
                "製品コード", "名前", "重量", "入数", "比重", 
                "外装", "顧客名", "ショット", "粘度", "製品サイズ"
            ]
            
            # Excel読み込み
            # dtype=objectを指定することで、勝手に数値変換してエラーになるのを防ぎます
            df_raw = pd.read_excel(
                uploaded_file, 
                sheet_name="製品一覧", 
                usecols=target_indices, 
                names=col_names,
                engine='openpyxl',
                dtype=object 
            )
            
            # calc.pyのロジックで分割処理を実行
            df_final = process_product_data(df_raw)
            
            # 結果表示
            st.success(f"抽出完了：{len(df_final)}件")
            st.subheader("📋 抽出データプレビュー")
            st.dataframe(df_final, use_container_width=True)

        except Exception as e:
            st.error(f"エラーが発生しました: {e}")
            st.warning("シート名が『製品一覧』であること、指定の列が存在することを確認してください。")

if __name__ == "__main__":
    main()main()main()
