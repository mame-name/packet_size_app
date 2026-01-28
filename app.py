import streamlit as st
import pandas as pd
import plotly.express as px
from calc import process_product_data

# --- 設定値（GitHubで調整可能） ---
LINE_WIDTH = 1
MARKER_SIZE = 6
PLOT_OPACITY = 0.8
# ------------------------------

st.set_page_config(layout="wide", page_title="小袋サイズ適正化アプリ")

def main():
    st.title("📦 製品サイズ適正化シミュレーター")

    # 画面を左右に分割 (1:1の比率)
    col_left, col_right = st.columns(2)

    # --- 左側：Excelアップロードと解析 ---
    with col_left:
        st.subheader("📁 エクセル解析")
        uploaded_file = st.file_uploader("実績XLSMファイルをアップロード", type=['xlsm'])
        
        df_final = None
        if uploaded_file:
            try:
                target_indices = [0, 1, 4, 5, 6, 9, 15, 17, 18, 25, 26]
                col_names = ["製品コード", "名前", "充填機", "重量", "入数", "比重", "外装", "顧客名", "ショット", "粘度", "製品サイズ"]
                df_raw = pd.read_excel(uploaded_file, sheet_name="製品一覧", usecols=target_indices, names=col_names, skiprows=5, engine='openpyxl', dtype=object)
                df_final = process_product_data(df_raw)
                st.success("解析完了")
            except Exception as e:
                st.error(f"エラー: {e}")

    # --- 右側：手入力シミュレーション ---
    with col_right:
        st.subheader("✍️ 手入力シミュレーション")
        with st.form("sim_form"):
            c1, c2 = st.columns(2)
            with c1:
                input_w = st.number_input("重量 (g)", value=0.0, format="%.2f")
                input_sg = st.number_input("比重", value=1.0, format="%.3f")
                input_machine = st.selectbox("充填機", ["通常機", "FR機"])
            with c2:
                input_width = st.number_input("巾 (mm)", value=0)
                input_length = st.number_input("長さ (mm)", value=0)
            
            submit = st.form_submit_button("計算実行")

        if submit:
            # シミュレーション計算
            sim_area = (input_width - 10) * input_length if "FR" in input_machine else (input_width - 8) * input_length
            sim_vol = input_w / input_sg if input_sg > 0 else 0
            sim_height = (sim_vol / sim_area) * 1000000 * 1.9 if sim_area > 0 else 0
            
            st.metric("算出された高さ", f"{sim_height:.2f}")
            
            # 安全判定の目安表示
            st.write(f"【計算詳細】 面積: {sim_area:,.0f} / 体積: {sim_vol:.4f}")

    st.divider()

    # --- グラフ表示（下部に全幅表示、またはデータがある場合のみ） ---
    if df_final is not None:
        st.subheader("📊 相関プロットとシミュレーション位置の確認")
        
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

            # 近似曲線を追加する関数
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

            # もしシミュレーション計算がされていたら、グラフに星印を追加
            if submit and sim_vol > 0 and sim_height > 0:
                fig.add_trace(go.Scatter(
                    x=[sim_vol], y=[sim_height],
                    mode='markers',
                    marker=dict(symbol='star', size=15, color='red', line=dict(width=2, color='black')),
                    name='シミュレーション点'
                ))

            fig.update_traces(marker=dict(size=MARKER_SIZE, opacity=PLOT_OPACITY, line=dict(width=0.5, color='white')), selector=dict(mode='markers'))
            fig.update_layout(xaxis=dict(tickformat=".3f"), yaxis=dict(dtick=1), height=600)
            
            st.plotly_chart(fig, use_container_width=True)
            
            st.subheader("📋 解析データ一覧")
            st.dataframe(df_final, use_container_width=True)

if __name__ == "__main__":
    main()
