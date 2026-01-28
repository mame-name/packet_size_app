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

# ラベルと入力を横並びにするためのカスタムCSS
st.markdown("""
    <style>
    [data-testid="stSidebar"] .stForm > div { border: none; padding: 0; }
    [data-testid="stSidebar"] .row-widget.stHorizontal { gap: 0.5rem; }
    /* ラベルのフォントサイズを少し小さく */
    [data-testid="stSidebar"] label { font-size: 0.9rem !important; }
    </style>
    """, unsafe_allow_html=True)

def main():
    # --- 左側：固定入力エリア (サイドバー) ---
    with st.sidebar:
        st.caption("📦 小袋サイズ適正化")
        
        # 1. エクセル解析（コンパクトに）
        uploaded_file = st.file_uploader("実績XLSM読込", type=['xlsm'], label_visibility="collapsed")
        
        st.divider()
        
        # 2. パラメータ入力（1行ずつ横並びに配置）
        with st.form("sim_form"):
            def input_row(label, placeholder=None, is_number=False):
                c1, c2 = st.columns([1, 2])
                with c1:
                    st.markdown(f"<div style='padding-top:10px;'>{label}</div>", unsafe_allow_html=True)
                with c2:
                    if is_number:
                        return st.number_input(label, value=0, step=5, label_visibility="collapsed")
                    else:
                        return st.text_input(label, placeholder=placeholder, label_visibility="collapsed")

            i_w = input_row("重量", "単位：g")
            i_sg = input_row("比重", "0.000")
            i_width = input_row("巾", "折り返し")
            i_length = input_row("長さ", is_number=True)
            
            c1, c2 = st.columns([1, 2])
            with c1: st.markdown("<div style='padding-top:10px;'>充填機</div>", unsafe_allow_html=True)
            with c2: i_machine = st.selectbox("機", ["通常", "FR"], label_visibility="collapsed")
            
            submit = st.form_submit_button("計算実行", use_container_width=True)

        # --- シミュレーション結果の表示（コンパクト版） ---
        sim_data = None
        if submit:
            try:
                w_val = float(i_w) if i_w else 0.0
                sg_val = float(i_sg) if i_sg else 0.0
                width_val = float(i_width) if i_width else 0.0
                length_val = float(i_length)
                
                if width_val > 0 and length_val > 0 and sg_val > 0:
                    sim_area = (width_val - 10) * length_val if "FR" in i_machine else (width_val - 8) * length_val
                    sim_vol = w_val / sg_val
                    sim_height = (sim_vol / sim_area) * 1000000 * 1.9
                    
                    sim_data = {"vol": sim_vol, "height": sim_height}
                    
                    st.markdown(f"""
                    <div style="background-color:#f0f2f6; padding:10px; border-radius:5px; margin-top:10px;">
                        <span style="font-size:0.8rem; color:#555;">結果</span><br>
                        <b>高さ: {sim_height:.2f}</b><br>
                        <b>体積: {sim_vol:.4f}</b>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.caption("⚠️ 数値を確認してください")
            except ValueError:
                st.caption("⚠️ 数値エラー")

    # --- 右側：メインパネル ---
    st.title("📊 解析パネル")

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

            if sim_data:
                fig.add_trace(go.Scatter(
                    x=[sim_data["vol"]], y=[sim_data["height"]],
                    mode='markers+text',
                    marker=dict(symbol='star', size=18, color='red', line=dict(width=2, color='black')),
                    name='現在値',
                    text=["★"], textposition="top center"
                ))

            fig.update_traces(marker=dict(size=MARKER_SIZE, opacity=PLOT_OPACITY, line=dict(width=0.5, color='white')), selector=dict(mode='markers'))
            fig.update_layout(xaxis=dict(tickformat=".3f"), yaxis=dict(dtick=1), height=700)
            st.plotly_chart(fig, use_container_width=True)
            
        st.subheader("📋 抽出データ詳細")
        st.dataframe(df_final, use_container_width=True)
    else:
        st.warning("左側のメニューからファイルをアップロードしてください。")

if __name__ == "__main__":
    main()
