import streamlit as st
import pandas as pd
import plotly.express as px
from calc import process_product_data

# 画面設定
st.set_page_config(layout="wide", page_title="小袋サイズ適正化アプリ")

def main():
    st.title("📦 製品リスト抽出・分析ツール")
    st.info("製品一覧から抽出したデータを基に、体積と高さの相関を可視化します。")

    uploaded_file = st.file_uploader("実績XLSMファイルをアップロード", type=['xlsm'])
    
    if uploaded_file:
        try:
            # 抽出対象列
            target_indices = [0, 1, 4, 5, 6, 9, 15, 17, 18, 25, 26]
            col_names = [
                "製品コード", "名前", "充填機", "重量", "入数", 
                "比重", "外装", "顧客名", "ショット", "粘度", "製品サイズ"
            ]
            
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
            
            # 結果表示
            st.success(f"データ処理完了：{len(df_final)} 件")

            # --- プロット図の作成 ---
            st.subheader("📊 体積 vs 高さ プロット図")
            
            # 数値データがない行をグラフ用から除外
            plot_df = df_final.dropna(subset=['体積', '高さ'])
            
            if not plot_df.empty:
                fig = px.scatter(
                    plot_df,
                    x="体積",
                    y="高さ",
                    hover_name="名前",  # 点にカーソルを置くと製品名を表示
                    hover_data=["製品コード", "充填機", "製品サイズ", "重量"],
                    color="充填機",     # 充填機ごとに色分け
                    title="体積と高さの相関（製品別）",
                    labels={"体積": "体積 (重量/比重)", "高さ": "算出された高さ"}
                )
                
                # グラフの見た目を調整
                fig.update_traces(marker=dict(size=10, opacity=0.7))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("グラフ表示に必要な数値データ（重量、比重、サイズ）が不足しています。")

            # データテーブル表示
            st.subheader("📋 抽出データ一覧")
            st.dataframe(df_final, use_container_width=True)

        except Exception as e:
            st.error(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    main()
