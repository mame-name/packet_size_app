import streamlit as st
import pandas as pd
from calc import process_product_data

# 画面の横幅を広く使う設定
st.set_page_config(layout="wide")

def main():
    st.title("📦 小袋サイズ適正化シミュレーター")
    st.markdown("実績XLSMファイルをアップロードして、袋サイズの最適化余地を分析します。")

    # ファイルアップローダー
    uploaded_file = st.file_uploader("実績XLSM（製品一覧シート）を選択してください", type=['xlsm'])
    
    if uploaded_file:
        try:
            # A, B, F, G, J, P, R, S, Z, AA 列のインデックス (0始まり)
            target_indices = [0, 1, 5, 6, 9, 15, 17, 18, 25, 26]
            col_names = [
                "製品コード", "名前", "重量", "入数", "比重", 
                "外装", "顧客名", "ショット", "粘度", "製品サイズ"
            ]
            
            # データ読み込み
            df_raw = pd.read_excel(
                uploaded_file, 
                sheet_name="製品一覧", 
                usecols=target_indices, 
                names=col_names,
                engine='openpyxl'
            )
            
            # calc.pyのロジックを実行
            df_processed = process_product_data(df_raw)
            
            # 結果の表示
            st.success(f"読み込み完了: {len(df_processed)} 件のデータを処理しました。")
            
            # データのプレビュー
            st.subheader("📊 取り込みデータ一覧")
            # 巾・長さ・面積が右側に追加された状態で見れる
            st.dataframe(df_processed, use_container_width=True)

            # ダウンロード機能
            csv = df_processed.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="処理済みデータをCSVで保存",
                data=csv,
                file_name="processed_product_data.csv",
                mime="text/csv",
            )

        except Exception as e:
            st.error(f"エラーが発生しました: {e}")
            st.info("シート名が「製品一覧」になっているか、列構成が正しいか確認してください。")

if __name__ == "__main__":
    main()
