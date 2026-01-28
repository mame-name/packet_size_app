import streamlit as st
import pandas as pd
import plotly.express as px
from calc import process_product_data

# 画面設定
st.set_page_config(layout="wide", page_title="小袋サイズ適正化アプリ")

def main():
    st.title("📦 製品リスト抽出・分析ツール")
    st.info("製品一覧からデータを抽出し、体積と高さの相関および累乗近似曲線を表示します。")

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
            
            # --- グラフ表示エリア ---
            st.subheader("📊 体積 vs 高さ 相関プロット（累乗近似曲線付き）")
            
            # 数値があるデータのみでプロット（近似計算のため0以下の値も除外）
            plot_df = df_final.dropna(subset=['体積', '高さ'])
            plot_df = plot_df[(plot_df['体積'] > 0) & (plot_df['高さ'] > 0)]
            
            if not plot_df.empty:
                # カスタムカラー（薄紫、黄緑、水色）
                custom_colors = ["#DDA0DD", "#7CFC00", "#00BFFF"]
                
                # trendline="ols" で対数軸を利用した累乗近似をシミュレート
                # ※Plotly Expressで直接「累乗」を指定する際は、対数変換を伴う最小二乗法を用います
                fig = px.scatter(
                    plot_df,
                    x="体積",
                    y="高さ",
                    hover_name="名前",
                    hover_data=["製品コード", "充填機", "製品サイズ", "重量"],
                    color="充填機",
                    color_discrete_sequence=custom_colors,
                    labels={"体積": "体積 (重量/比重)", "高さ": "高さ (計算値)"},
                    range_x=[0, 0.04], 
                    range_y=[0, 10],
                    trendline="ols",             # 近似曲線を追加
                    trendline_options=dict(log_x=True, log_y=True) # 累乗近似(y=ax^b)の設定
                )
                
                # プロットの点と線の設定
                fig.update_traces(
                    marker=dict(size=6, opacity=0.8, line=dict(width=0.5, color='white'))
                )
                
                # レイアウト設定
                fig.update_layout(
                    xaxis=dict(tickformat=".3f"),
                    yaxis=dict(dtick=1),
                    legend_title_text='充填機タイプ'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # 近似曲線の詳細（R2値など）を表示したい場合は以下のコメントを外す
                # results = px.get_trendline_results(fig)
                # st.write(results.px_fit_results.iloc[0].summary())
                
            else:
                st.warning("プロットに必要な数値データが不足しています。")

            # --- データテーブル表示 ---
            st.subheader("📋 抽出データ一覧")
            st.dataframe(df_final, use_container_width=True)

        except Exception as e:
            st.error(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    main()
