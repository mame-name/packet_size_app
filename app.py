import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from calc import process_product_data

# --- 設定値（GitHubで調整可能） ---
LINE_WIDTH = 1
MARKER_SIZE = 6
PLOT_OPACITY = 0.8
# ------------------------------

# 画面全体のレイアウト設定
st.set_page_config(layout="wide", page_title="小袋サイズ適正化アプリ")

def main():
    # --- 左側：固定入力エリア (サイドバー) ---
    # 比率的に30%程度を占め、メイン画面のスクロールに影響されません
    with st.sidebar:
        st.title("📥 入力・設定")
        
        st.subheader("1. エクセル解析")
        uploaded_file = st.file_uploader("実績XLSMをアップロード", type=['xlsm'])
        
        st.divider()
        
        st.subheader("2. シミュレーション")
        with st.form("sim_form"):
            input_w = st.number_input("重量 (g)", value=0.0, format="%.2f")
            input_sg = st.number_input("比重", value=1.0, format="%.3f")
            input_width = st.number_input("巾 (mm)", value=0)
            input_length = st.number_input("長さ (mm)", value=0)
            input_machine = st.selectbox("充填機", ["通常機", "FR機"])
            
            submit = st.form_submit_button("シミュレーション実行")

    # --- 右側：解析結果表示エリア (メインパネル) ---
    # ここはデータ量が増えると縦にスクロールします
    st.title("📊 解析・シミュレーション結果")

    df_final = None
    if uploaded_file:
        try:
            target_indices = [0, 1, 4, 5, 6, 9, 15, 17, 18, 25, 26]
            col_names = ["製品コード", "名前", "充填機", "重量", "入数", "比重", "外装", "顧客名", "ショット", "粘度", "製品サイズ"]
            df_raw = pd.read_excel(uploaded_file, sheet_name="製品一覧", usecols=target_indices, names=col_names, skiprows=5, engine='openpyxl', dtype=object)
            df_final = process_product_data(df_raw)
        except Exception as e:
            st.error(f"Excel解析エラー: {e}")

    # メインコンテンツの描画
    if df_final is not None:
        # グラフセクション
        st.subheader("📉 相関プロット（全体近似曲線付き）")
        
        plot_df = df_final.dropna(subset=['体積', '高さ', '上限高', '下限高'])
        plot_df = plot_df[(plot_df['体積'] > 0) & (plot_df['高さ'] > 0)].copy()

        if not plot_df.empty:
            custom_colors = ["#DDA0DD", "#7CFC00", "#00BFFF"]
            fig = px.scatter(
                plot_df, x="体積", y="高さ", color="充填機",
                hover_name="名前", color_discrete_sequence=custom_colors,
                range_x=[0, 0.04], range_y=[0, 10],
                labels={"体積": "体積", "高さ": "高さ"}
            )

            # 近似曲線を追加
            def add_trend(y_col, name, color):
                temp_fig = px.scatter(plot_df, x="体積", y=y_col, trendline="ols", trendline_options=dict(log_x=True, log_y=True))
                trend = temp_fig.data[1]
                trend.name = name
                trend.line.color = color
                trend.line.width = LINE_WIDTH
                fig.add_trace(trend)

            add_trend("高さ", "全体平均", "DarkSlateGrey")
            add_trend("上限高", "上限目安", "Orange")
            add_trend("下限高", "下限目安", "DeepPink")

            # シミュレーション点の追加
            if submit and input_width > 0 and input_length > 0:
                sim_area = (input_width - 10) * input_length if "FR" in input_machine else (input_width - 8) * input_length
                sim_vol = input_w / input_sg if input_sg > 0 else 0
                sim_height = (sim_vol / sim_area) * 1000000 * 1.9 if sim_area > 0 else 0
                
                fig.add_trace(go.Scatter(
                    x=[sim_vol], y=[sim_height],
                    mode='markers+text',
                    marker=dict(symbol='star', size=18, color='red', line=dict(width=2, color='black')),
                    name='シミュレーション結果',
                    text=["★現在値"], textposition="top center"
                ))
                st.info(f"💡 シミュレーション結果 → 高さ: **{sim_height:.2f}** / 体積: **{sim_vol:.4f}**")

            fig.update_traces(marker=dict(size=MARKER_SIZE, opacity=PLOT_OPACITY, line=dict(width=0.5, color='white')), selector=dict(mode='markers'))
            fig.update_layout(xaxis=dict(tickformat=".3f"), yaxis=dict(dtick=1), height=700)
            st.plotly_chart(fig, use_container_width=True)
            
        # テーブルセクション
        st.subheader("📋 抽出データ詳細")
        st.dataframe(df_final, use_container_width=True)
    else:
        st.warning("左側のメニューから実績ファイルをアップロードしてください。")

if __name__ == "__main__":
    main()
