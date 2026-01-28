import streamlit as st
import pandas as pd
from calc import process_product_data

# 画面設定：横幅を広く使い、タイトルを設定
st.set_page_config(layout="wide", page_title="小袋サイズ適正化アプリ")

def main():
    st.title("📦 製品リスト抽出・分割ツール")
    st.info("「製品一覧」シートから指定列を抽出し、サイズが記載されているデータのみを表示します。")

    # ファイルアップローダーの設定
    uploaded_file = st.file_uploader("実績XLSMファイルをアップロードしてください", type=['xlsm'])
    
    if uploaded_file:
        try:
            # 抽出対象列のインデックス（A=0, B=1, F=5, G=6, J=9, P=15, R=17, S=18, Z=25, AA=26）
            target_indices = [0, 1, 5, 6, 9, 15, 17, 18, 25, 26]
            
            # 独立した列名として定義
            col_names = [
                "製品コード", "名前", "重量", "入数", "比重", 
                "外装", "顧客名", "ショット", "粘度", "製品サイズ"
            ]
            
            # Excelの読み込み（dtype=objectで型を固定せず取り込む）
            df_raw = pd.read_excel(
                uploaded_file, 
                sheet_name="製品一覧", 
                usecols=target_indices, 
                names=col_names,
                engine='openpyxl',
                dtype=object 
            )
            
            # calc.pyのロジックでフィルタリングと分割を実行
            df_final = process_product_data(df_raw)
            
            # 画面表示
            st.success(f"有効データ抽出完了：{len(df_final)} 件")
            
            st.subheader("📋 抽出データプレビュー")
            # 巾と長さが最後に追加された状態で表示される
            st.dataframe(df_final, use_container_width=True)

            # CSVダウンロードボタン（確認用）
            csv = df_final.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="抽出データをCSVで保存",
                data=csv,
                file_name="extracted_products.csv",
                mime="text/csv",
            )

        except Exception as e:
            st.error(f"エラーが発生しました: {e}")
            st.warning("シート名が『製品一覧』であること、指定の列が存在することを確認してください。")

if __name__ == "__main__":
    main()
