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

st.set_page_config(layout="wide", page_title="小袋サイズ適正化アプリ")

def main():
    # --- 左側：固定入力エリア (サイドバー 約3:7の比率で固定されます) ---
    with st.sidebar:
        st.title("📥 入力・設定")
        
        st.subheader("1. エクセル解析")
        uploaded_file = st.file_uploader("実績XLSMをアップロード", type=['xlsm'])
        
        st.divider()
        
        st.subheader("2. シミュレーション")
        with st.form("sim_form"):
            # 重量・比重・巾はボタンなしのテキスト入力（プレースホルダー付き）
            input_w = st.text_input("重量", placeholder="単位：g")
            input_sg = st.text_input("比重", placeholder="0.000")
            input_width = st.text_input("巾", placeholder="折返し巾・単位：mm")
            
            # 長さのみ +/- ボタン付き、5単位で動く設定
            input_length = st.number_input("長さ (mm)", placeholder="単位：mm", value=0, step=5)
            
            input_machine = st.selectbox("充填機", ["FR-1/5", "ZERO-1"])
            
            submit = st.form_submit_button("シミュレーション実行")

    # --- 右側：解析結果表示エリア (メインパネル / スクロール可能) ---
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

    if df_final is not None:
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

            # 近似曲線追加関数
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

            # シミュレーション値の反映
            if submit:
                try:
                    # テキスト入力値を数値に変換
                    w_val = float(input_w) if input_w else 0.0
                    sg_val = float(input_sg) if input_sg else 0.0
                    width_val = float(input_width) if input_width else 0.0
                    length_val = float(input_length) # number_inputなのでそのまま数値
                    
                    if width_val > 0 and length_val > 0 and sg_val > 0:
                        sim_area = (width_val - 10) * length_val if "FR" in input_machine else (width_val - 8) * length_val
                        sim_vol = w_val / sg_val
                        sim_height = (sim_vol / sim_area) * 1000000 * 1.9
                        
                        # グラフに★を追加
                        fig.add_trace(go.Scatter(
                            x=[sim_vol], y=[sim_height],
                            mode='markers+text',
                            marker=dict(symbol='star', size=18, color='red', line=dict(width=2, color='black')),
                            name='シミュレーション結果',
                            text=["★現在値"], textposition="top center"
                        ))
                        st.info(f"💡 シミュレーション結果 → 高さ: **{sim_height:.2f}** / 体積: **{sim_vol:.4f}**")
                    else:
                        st.warning("各項目に0より大きい数値を入力してください。")
                except ValueError:
                    st.warning("数値として正しくない入力があります。")

            fig.update_traces(marker=dict(size=MARKER_SIZE, opacity=PLOT_OPACITY, line=dict(width=0.5, color='white')), selector=dict(mode='markers'))
            fig.update_layout(xaxis=dict(tickformat=".3f"), yaxis=dict(dtick=1), height=700)
            st.plotly_chart(fig, use_container_width=True)
            
        st.subheader("📋 抽出データ詳細")
        st.dataframe(df_final, use_container_width=True)
    else:
        st.warning("左側のメニューから実績ファイルをアップロードしてください。")

if __name__ == "__main__":
    main()
