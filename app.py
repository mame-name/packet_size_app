import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from calc import process_product_data

# ==========================================
# グラフの表示詳細設定（ここを書き換えて調整）
# ==========================================
LINE_WIDTH = 0.5           # 近似曲線の太さ
MARKER_SIZE = 6          # プロットの点の大きさ
PLOT_OPACITY = 0.8       # プロットの透明度
# ==========================================

st.set_page_config(layout="wide", page_title="小袋サイズ適正化アプリ")

def main():
    st.title("📦 製品リスト抽出・分析ツール")
    st.info(f"近似曲線の太さ: {LINE_WIDTH}px で描画中。GitHubのコード内で数値を調整可能です。")

    uploaded_file = st.file_uploader("実績XLSMファイルをアップロード", type=['xlsm'])
    
    if uploaded_file:
        try:
            target_indices = [0, 1, 4, 5, 6, 9, 15, 17, 18, 25, 26]
            col_names = ["製品コード", "名前", "充填機", "重量", "入数", "比重", "外装", "顧客名", "ショット", "粘度", "製品サイズ"]
            
            df_raw = pd.read_excel(uploaded_file, sheet_name="製品一覧", usecols=target_indices, names=col_names, skiprows=5, engine='openpyxl', dtype=object)
            df_final = process_product_data(df_raw)
            
            st.subheader("📊 相関プロットと全体累乗近似")
            
            plot_df = df_final.dropna(subset=['体積', '高さ', '上限高', '下限高'])
            plot_df = plot_df[(plot_df['体積'] > 0) & (plot_df['高さ'] > 0) & (plot_df['上限高'] > 0) & (plot_df['下限高'] > 0)].copy()
            
            if not plot_df.empty:
                # 1. 散布図作成
                custom_colors = ["#DDA0DD", "#7CFC00", "#00BFFF"]
                fig = px.scatter(
                    plot_df, x="体積", y="高さ", color="充填機",
                    hover_name="名前", color_discrete_sequence=custom_colors,
                    range_x=[0, 0.04], range_y=[0, 10],
                    labels={"体積": "体積", "高さ": "高さ"}
                )

                # 2. 全体近似曲線の計算
                def get_trendline(y_col, name, color):
                    temp_fig = px.scatter(plot_df, x="体積", y=y_col, 
                                        trendline="ols", 
                                        trendline_options=dict(log_x=True, log_y=True))
                    trend = temp_fig.data[1]
                    trend.name = name
                    trend.line.color = color
                    trend.line.dash = "solid"
                    trend.line.width = LINE_WIDTH # 定数を適用
                    return trend

                # 近似曲線の追加
                fig.add_trace(get_trendline("高さ", "高さ近似", "DarkSlateGrey"))
                fig.add_trace(get_trendline("上限高", "上限近似", "Orange"))
                fig.add_trace(get_trendline("下限高", "下限近似", "DeepPink"))
                
                # 点のスタイル調整
                fig.update_traces(
                    marker=dict(size=MARKER_SIZE, opacity=PLOT_OPACITY, line=dict(width=0.5, color='white')),
                    selector=dict(mode='markers')
                )
                
                fig.update_layout(
                    xaxis=dict(tickformat=".3f"),
                    yaxis=dict(dtick=1),
                    legend_title_text='凡例'
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("有効な計算データが不足しています。")

            st.subheader("📋 抽出データ一覧")
            st.dataframe(df_final, use_container_width=True)

        except Exception as e:
            st.error(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    main()
