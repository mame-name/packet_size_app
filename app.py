import streamlit as st
import pandas as pd
from calc import process_product_data

# 画面設定
st.set_page_config(layout="wide", page_title="小袋サイズ適正化アプリ")

def main():
    st.title("📦 製品リスト抽出・分割ツール")
    st.info("「製品一覧」シートの6行目以降から指定の11列を抽出し、サイズを分割表示します。")

    uploaded_file = st.file_uploader("実績XLSMファイルをアップロード", type=['xlsm'])
    
    if uploaded_file:
        try:
            # 抽出対象列のインデックス（元データの並び順）
            # A=0, B=1, E=4, F=5, G=6, J=9, P=15, R=17, S=18, Z=25, AA=26
            target_indices = [0, 1, 4, 5, 6, 9, 15, 17, 18, 25, 26]
            
            # 列名の定義（インデックスの順番に対応）
            col_names = [
                "製品コード", "名前", "充填機", "重量", "入数", 
                "比重", "外装", "顧客名", "ショット", "粘度", "製品サイズ"
            ]
            
            # Excel読み込み（skiprows=5 で 6行目から開始）
            df_raw = pd.read_excel(
                uploaded_file, 
                sheet_name="製品一覧", 
                usecols=target_indices, 
                names=col_names,
                skiprows=5,
                engine='openpyxl',
                dtype=object 
            )
            
            # ロジック実行（フィルタリングと分割）
            df_final = process_product_data(df_raw)
            
            # 画面表示
            st.success(f"抽出完了：有効データ {len(df_final)} 件")
            st.subheader("📋 抽出データプレビュー")
            # 充填機が「名前」と「重量」の間に配置された状態で表示されます
            st.dataframe(df_final, use_container_width=True)

            # CSVダウンロードボタン
            csv = df_final.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="抽出データをCSVで保存",
                data=csv,
                file_name="extracted_products_with_machine.csv",
                mime="text/csv",
            )

        except Exception as e:
            st.error(f"エラーが発生しました: {e}")
            st.warning("シート名が『製品一覧』であること、6行目にデータがあることを確認してください。")

if __name__ == "__main__":
    main()
