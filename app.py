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

# カスタムCSS: コンパクト化
st.markdown("""
    <style>
    [data-testid="stSidebar"] .stForm { border: none; padding: 0; }
    [data-testid="stSidebar"] .element-container { margin-bottom: -5px; }
    [data-testid="stSidebar"] label { font-size: 0.85rem !important; }
    </style>
    """, unsafe_allow_html=True)

def main():
    # --- 左側：固定入力エリア (サイドバー) ---
    with st.sidebar:
        st.caption("📦 小袋サイズ適正化")
        
        # 1. エクセル解析
        uploaded_file = st.file_uploader("実績XLSM読込", type=['xlsm'], label_visibility="collapsed")
        
        st.divider()

        # 結果表示用のプレースホルダーを先に作成
        result_container = st.container()

        # 2. パラメータ入力
        with st.form("sim_form"):
            def input_row(label, placeholder=None, is_number=False):
                c1, c2 = st.columns([1, 2])
                with c1:
                    st.markdown(f"<div style='padding-top:8px;'>{label}</div>", unsafe_allow_html=True)
                with c2:
                    if is_number:
                        return st.number_input(label, value=0, step=5, label_visibility="collapsed")
                    else:
                        return st.text_input(label, placeholder=placeholder, label_visibility="collapsed")

            i_w = input_row("重量", "g")
            i_sg = input_row("比重", "0.000")
            i_width = input_row("巾", "折り返し")
            i_length = input_row("長さ", is_number=True)
            
            c1, c2 = st.columns([1, 2])
            with c1: st.markdown("<div style='padding-top:8px;'>充填機</div>", unsafe_allow_html=True)
            with c2: i_machine = st.selectbox("機", ["FR-1/5", "ZERO-1"], label_visibility="collapsed")
            
            submit = st.form_submit_button("計算実行", use_container_width=True)

        # 計算処理と結果表示
        sim_data = None
        if submit:
            try:
                w_v = float(i_w) if i_w else 0.0
                s_v = float(i_sg) if i_sg else 0.0
                wd_v = float(i_width) if i_width else 0.0
                ln_v = float(i_length)
                
                if wd_v > 0 and ln_v > 0 and s_v > 0:
                    area = (wd_v - 10) * ln_v if "FR" in i_machine else (wd_v - 8) * ln_v
                    vol = w_v / s_v
                    height = (vol / area) * 1000000 * 1.9
                    sim_data = {"vol": vol, "height": height}
                    
                    # フォームより上のコンテナに結果を書き込む
                    result_container.markdown(f"""
                    <div style="background-color:#f0f2f6; padding:8px; border-radius:5px; margin-bottom:15px; border-left: 5px solid #00BFFF;">
                        <span style="font-size:0.75rem; color:#666;">最新の計算結果</span><br>
                        <span style="font-size:0.9rem;">高さ: <b>{height:.2f}</b></span> / 
                        <span style="font-size:0.9rem;">体積: <b>{vol:.4f}</b></span>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    result_container.error("数値を入力してください")
            except ValueError:
                result_container.error("入力エラー")
        else:
            result_container.caption("結果がここに表示されます")

    # --- 右側：メインパネル ---
    st.title("📊 解析パネル")

    if uploaded_file:
        try:
            target_indices = [0, 1, 4, 5, 6, 9, 15, 17, 18, 25, 26]
            col_names = ["製品コード", "名前", "充填機", "重量", "入数", "比重", "外装", "顧客名", "ショット", "粘度", "製品サイズ"]
            df_raw = pd.read_excel(uploaded_file, sheet_name="製品一覧", usecols=target_indices, names=col_names, skiprows=5, engine='openpyxl', dtype=object)
            df_final = process_product_data(df_raw)
            
            # グラフ表示
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
                    # 全データに対して1本のトレンドラインを計算
                    temp_fig = px.scatter(plot_df, x="体積", y=y_col, trendline="ols", trendline_options=dict(log_x=True, log_y=True))
                    trend = temp_fig.data[1]
                    trend.name = name
                    trend.line.color = color
                    trend.line.width = LINE_WIDTH
                    fig.add_trace(trend)

                add_trend("高さ", "全体平均", "DarkSlateGrey")
                add_trend("上限高", "上限目安", "Orange")
                add_trend("下限高", "下限目安", "DeepPink")

                # ★のプロット
                if sim_data:
                    fig.add_trace(go.Scatter(
                        x=[sim_data["vol"]], y=[sim_data["height"]],
                        mode='markers+text',
                        marker=dict(symbol='star', size=18, color='red', line=dict(width=2, color='black')),
                        name='現在値', text=["★"], textposition="top center"
                    ))

                fig.update_traces(marker=dict(size=6, opacity=0.8, line=dict(width=0.5, color='white')), selector=dict(mode='markers'))
                fig.update_layout(xaxis=dict(tickformat=".3f"), yaxis=dict(dtick=1), height=700)
                st.plotly_chart(fig, use_container_width=True)
            
            st.subheader("📋 抽出データ詳細")
            st.dataframe(df_final, use_container_width=True)

        except Exception as e:
            st.error(f"エラーが発生しました: {e}")
    else:
        st.warning("左側のメニューからファイルをアップロードしてください。")

if __name__ == "__main__":
    main()
