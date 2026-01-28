import streamlit as st
import pandas as pd
import plotly.express as px
from calc import process_product_data

# 画面設定
st.set_page_config(layout="wide", page_title="小袋サイズ適正化アプリ")

def main():
    st.title("📦 製品リスト抽出・分析ツール")
    st.info("製品一覧の6行目以降からデータを抽出し、体積と高さの相関をプロットします。")

    uploaded_file = st.file_uploader("実績XLSMファイルをアップロードしてください", type=['xlsm'])
    
    if uploaded_file:
        try:
            # 抽出対象列（A, B, E, F, G, J, P, R, S, Z, AA）
            target_indices = [0, 1, 4, 5, 6, 9, 15, 17, 18, 25, 26]
            col_names = [
                "製品コード", "名前", "充填機", "重量", "入数", 
                "比重", "外装", "顧客名", "ショット", "粘度", "製品サイズ"
            ]
            
            # Excel読み込み
            df_raw = pd.read_excel(
                uploaded_file, 
                sheet_name="製品一覧", 
                usecols=target_indices, 
                names=col_names,
                skiprows=5,
                engine='openpyxl',
                dtype=object 
            )
            
            # calc.pyのロジック実行
            df_final = process_product_data(df_raw)
            
            # 1. グラフ表示エリア
            st.subheader("📊 体積 vs 高さ 相関プロット")
            
            # 数値があるデータのみでプロット
            plot_df = df_final.dropna(subset=['体積', '高さ'])
            
            if not plot_df.empty:
                fig = px.scatter(
                    plot_df,
                    x="体積",
                    y="高さ",
                    hover_name="名前",
                    hover_data=["製品コード", "充填機", "製品サイズ", "重量"],
                    color="充填機",
                    labels={"体積": "体積 (重量/比重)", "高さ": "高さ (計算値)"}
                )
                fig.update_traces(marker=dict(size=12, opacity=0.7, line=dict(width=1, color='DarkSlateGrey')))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("プロットに必要な数値データが不足しています。")

            # 2. データテーブル表示
            st.subheader("📋 抽出データ一覧")
            st.dataframe(df_final, use_container_width=True)

            # CSVダウンロード
            csv = df_final.to_csv(index=False).encode('utf-8-sig')
            st.download_button("抽出データをCSVで保存", csv, "extracted_data.csv", "text/csv")

        except Exception as e:
            st.error(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    main()
