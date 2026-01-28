import streamlit as st
import pandas as pd
import plotly.express as px
from calc import process_product_data

st.set_page_config(layout="wide", page_title="小袋サイズ適正化アプリ")

def main():
    st.title("📦 製品リスト抽出・分析ツール")
    st.info("体積・高さに加え、上限・下限の近似曲線を表示します。")

    uploaded_file = st.file_uploader("実績XLSMファイルをアップロード", type=['xlsm'])
    
    if uploaded_file:
        try:
            target_indices = [0, 1, 4, 5, 6, 9, 15, 17, 18, 25, 26]
            col_names = ["製品コード", "名前", "充填機", "重量", "入数", "比重", "外装", "顧客名", "ショット", "粘度", "製品サイズ"]
            
            df_raw = pd.read_excel(uploaded_file, sheet_name="製品一覧", usecols=target_indices, names=col_names, skiprows=5, engine='openpyxl', dtype=object)
            df_final = process_product_data(df_raw)
            
            st.subheader("📊 相関プロットと累乗近似（上限・下限）")
            
            # グラフ用データ（正の値のみ）
            plot_df = df_final.dropna(subset=['体積', '高さ', '上限高', '下限高'])
            plot_df = plot_df[(plot_df['体積'] > 0) & (plot_df['高さ'] > 0) & (plot_df['上限高'] > 0) & (plot_df['下限高'] > 0)].copy()
            
            if not plot_df.empty:
                # 1. メインの散布図（高さ）
                fig = px.scatter(
                    plot_df, x="体積", y="高さ", color="充填機",
                    hover_name="名前", color_discrete_sequence=["#DDA0DD", "#7CFC00", "#00BFFF"],
                    range_x=[0, 0.04], range_y=[0, 10],
                    labels={"体積": "体積", "高さ": "高さ"},
                    trendline="ols", trendline_options=dict(log_x=True, log_y=True)
                )
                fig.data[-1].name = "高さ近似"
                fig.data[-1].line.color = "gray"

                # 2. 上限高の近似曲線
                fig_up = px.scatter(plot_df, x="体積", y="上限高", trendline="ols", trendline_options=dict(log_x=True, log_y=True))
                trend_up = fig_up.data[1]
                trend_up.name = "上限近似"
                trend_up.line.color = "red" # 上限は赤（今後用とのことですが、一旦線として使用）
                fig.add_trace(trend_up)

                # 3. 下限高の近似曲線
                fig_down = px.scatter(plot_df, x="体積", y="下限高", trendline="ols", trendline_options=dict(log_x=True, log_y=True))
                trend_down = fig_down.data[1]
                trend_down.name = "下限近似"
                trend_down.line.color = "blue"
                fig.add_trace(trend_down)

                fig.update_traces(marker=dict(size=6, opacity=0.8, line=dict(width=0.5, color='white')), selector=dict(mode='markers'))
                fig.update_layout(xaxis=dict(tickformat=".3f"), yaxis=dict(dtick=1))
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("有効な計算データが不足しています。")

            st.subheader("📋 抽出データ一覧")
            st.dataframe(df_final, use_container_width=True)

        except Exception as e:
            st.error(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    main()
