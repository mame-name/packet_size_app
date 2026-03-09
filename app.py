import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from calc import process_product_data

# ==========================================
# グラフの表示詳細設定
# ==========================================
LINE_WIDTH = 1           
MARKER_SIZE = 6          
SIM_MARKER_SIZE = 15     
PLOT_OPACITY = 0.8       
# ==========================================

st.set_page_config(layout="wide", page_title="小袋サイズ適正化アプリ")

st.markdown("""
    <style>
    [data-testid="stSidebar"] .stForm { border: none; padding: 0; }
    [data-testid="stSidebar"] .element-container { margin-bottom: -5px; }
    [data-testid="stSidebar"] label { font-size: 0.85rem !important; }
    </style>
    """, unsafe_allow_html=True)

def main():
    # セッション状態の初期化（クリアボタン用）
    if 'reset_key' not in st.session_state:
        st.session_state.reset_key = 0

    with st.sidebar:
        st.subheader("📁 実績データ読込")
        uploaded_file = st.file_uploader("実績XLSM読込", type=['xlsm'], label_visibility="collapsed")

        # フォームの代わりにコンテナを使用（クリア機能を有効にするため）
        with st.container():
            def input_row(label, key, placeholder=None, is_number=False):
                c1, c2 = st.columns([1, 2])
                with c1: st.markdown(f"<div style='padding-top:8px;'>{label}</div>", unsafe_allow_html=True)
                with c2:
                    # キーにreset_keyを混ぜることで、リセット時にまるごと初期化される
                    unique_key = f"{key}_{st.session_state.reset_key}"
                    if is_number: return st.number_input(label, value=0, step=5, label_visibility="collapsed", key=unique_key)
                    else: return st.text_input(label, placeholder=placeholder, label_visibility="collapsed", key=unique_key)

            i_w = input_row("　重量", "w", "g")
            i_sg = input_row("　比重", "sg", "0.000")
            i_width = input_row("　巾", "wd", "折返し巾")
            i_length = input_row("　長さ", "ln", is_number=True)
            
            # シール
            c1, c2 = st.columns([1, 2])
            with c1: st.markdown("<div style='padding-top:8px;'>　シール</div>", unsafe_allow_html=True)
            with c2: i_seal = st.selectbox("　シール", ["ビン口", "フラット"], label_visibility="collapsed", key=f"seal_{st.session_state.reset_key}")

            # 充填機
            c1, c2 = st.columns([1, 2])
            with c1: st.markdown("<div style='padding-top:8px;'>　充填機</div>", unsafe_allow_html=True)
            with c2: i_machine = st.selectbox("　充填機", ["FR-1/5", "ZERO-1"], label_visibility="collapsed", key=f"mach_{st.session_state.reset_key}")
            
            # ボタン配置
            submit = st.button("計算実行", use_container_width=True, type="primary")
            if st.button("入力内容をクリア", use_container_width=True):
                st.session_state.reset_key += 1
                st.rerun()
                
        result_container = st.container()
        
        sim_data = None
        if submit:
            try:
                w_v, s_v, wd_v, ln_v = float(i_w or 0), float(i_sg or 0), float(i_width or 0), float(i_length or 0)
                if wd_v > 0 and ln_v > 0 and s_v > 0:
                    # シミュレーション用面積計算ロジック (calc.pyと同一)
                    adj_wd = (wd_v - 10) if "FR" in i_machine else (wd_v - 8)
                    
                    if i_seal == "フラット":
                        sim_area = adj_wd * (ln_v - 15)
                    else: # ビン口
                        sim_area = (adj_wd * (ln_v - 24)) + 40
                    
                    sim_vol = w_v / 1000 / s_v
                    sim_height = (sim_vol / sim_area) * 1000000 * 1.9
                    sim_data = {"vol": sim_vol, "height": sim_height}

                    result_container.markdown(f"""
                    <div style="background-color:#f0f2f6; padding:8px; border-radius:5px; margin-bottom:15px; border-left: 5px solid #00BFFF;">
                        <span style="font-size:0.9rem;">高さ: <b>{sim_height:.2f}</b></span> / 
                        <span style="font-size:0.9rem;">体積: <b>{sim_vol:.4f}</b></span>
                    </div>""", unsafe_allow_html=True)
                else: result_container.error("すべての項目を入力")
            except ValueError: result_container.error("入力エラー")

    st.markdown("<h1 style='text-align: center;'>Intelligent 熊谷さん<br>🤖 🤖 🤖 小袋サイズ確認 🤖 🤖 🤖</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>まるで熊谷さんが考えたような精度で小袋サイズを確認してくれるアプリです</p>", unsafe_allow_html=True)
    st.markdown("---")

    if uploaded_file:
        try:
            # AC列(28)を読み込み対象に追加
            target_indices = [0, 1, 4, 5, 6, 9, 15, 17, 18, 25, 26, 28]
            # 最初から「シール」として読み込む
            col_names = ["製品コード", "名前", "充填機", "重量", "入数", "比重", "外装", "顧客名", "ショット", "粘度", "製品サイズ", "シール"]
            df_raw = pd.read_excel(uploaded_file, sheet_name="製品一覧", usecols=target_indices, names=col_names, skiprows=5, engine='openpyxl', dtype=object)
            df_final = process_product_data(df_raw)
            
            plot_df = df_final.dropna(subset=['体積', '高さ', '上限高', '下限高'])
            plot_df = plot_df[(plot_df['体積'] > 0) & (plot_df['高さ'] > 0)].copy()

            if not plot_df.empty:
                fig = px.scatter(plot_df, x="体積", y="高さ", color="充填機", 
                                 hover_name="名前", 
                                 hover_data=["重量", "シール", "製品サイズ"],
                                 color_discrete_sequence=["#DDA0DD", "#7CFC00", "#00BFFF"],
                                 labels={"体積": "体積", "高さ": "高さ"})

                def add_trend(y_col, name, color):
                    temp_fig = px.scatter(plot_df, x="体積", y=y_col, trendline="ols", trendline_options=dict(log_x=True, log_y=True))
                    trend = temp_fig.data[1]
                    trend.name, trend.line.color, trend.line.width, trend.mode = name, color, LINE_WIDTH, 'lines'
                    fig.add_trace(trend)

                for col, n, c in [("高さ", "全体平均", "DarkSlateGrey"), ("上限高", "上限目安", "Orange"), ("下限高", "下限目安", "DeepPink")]:
                    add_trend(col, n, c)

                if sim_data:
                    fig.add_trace(go.Scatter(x=[sim_data["vol"]], y=[sim_data["height"]], mode='markers',
                                             marker=dict(symbol='star', size=SIM_MARKER_SIZE, color='red', line=dict(width=1.5, color='black')),
                                             name='シミュレーション結果'))

                # 軸固定・ズーム制限
                fig.update_layout(
                    xaxis=dict(tickformat=".3f", range=[0.0015, 0.04], autorange=False, minallowed=0),
                    yaxis=dict(dtick=1, range=[2.5, 12], autorange=False, minallowed=0),
                    height=700,
                    legend=dict(orientation="h", yanchor="top", y=-0.12, xanchor="center", x=0.5)
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            st.subheader("📋 抽出データ詳細")
            st.dataframe(df_final, use_container_width=True)

        except Exception as e: st.error(f"エラー: {e}")
    else: 
        st.info("👈 左側のパネルから「実績データベース (.xlsm)」をアップロードしてください。")

if __name__ == "__main__": main()
