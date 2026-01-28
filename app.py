import streamlit as st
import pandas as pd
from calc import process_product_data

# 画面設定
st.set_page_config(layout="wide", page_title="小袋サイズ適正化アプリ")

def main():
    st.title("📦 製品リスト抽出・分割ツール")
    st.info("「製品一覧」シートの6行目以降を読み込み、サイズがあるデータのみを表示します。")

    uploaded_file = st.file_uploader("実績XLSMファイルをアップロード", type=['xlsm'])
    
    if uploaded_file:
        try:
            # A, B, F, G, J, P, R, S, Z, AA 列のインデックス
            target_indices = [0, 1, 5, 6, 9, 15, 17, 18, 25, 26]
            
            # 6行目を項目名として扱うために5行スキップ
            # 名前をこちらで定義し直すため、namesを指定
            col_names = [
                "製品コード", "名前", "重量", "入数", "比重", 
                "外装", "顧客名", "ショット", "粘度", "製品サイズ"
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
            
            # ロジック実行
            df_final = process_product_data(df_raw)
            
            # 画面表示
            st.success(f"6行目以降から有効データ {len(df_final)} 件を抽出しました。")
            st.subheader("📋 抽出データプレビュー")
            st.dataframe(df_final, use_container_width=True)

            # CSVダウンロードボタン
            csv = df_final.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="抽出データをCSVで保存",
                data=csv,
                file_name="extracted_products.csv",
                mime="text/csv",
            )

        except Exception as e:
            st.error(f"エラーが発生しました: {e}")
            st.warning("シート名が『製品一覧』であること、6行目にデータが並んでいるか確認してください。")

if __name__ == "__main__":
    main()
