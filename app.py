
import streamlit as st
import pandas as pd

def main():
    st.title("小袋サイズ適正化シミュレーター")

    # データ取り込み（実績データ）
    uploaded_file = st.file_uploader("実績CSVをアップロード", type=['csv'])
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        # バッチサイズ計算（前回のロジック）
        df['batch_size'] = df['total_weight'] / df['actual_bags']
        
        # 比重設定（ユーザー入力）
        density = st.sidebar.number_input("中身の比重 (g/cm3)", value=0.5)
        
        # サイズ適正化の適用
        results = df['batch_size'].apply(lambda x: calculate_package_size(x, density))
        df_results = pd.concat([df, pd.DataFrame(list(results))], axis=1)
        
        st.write("### 最適化結果", df_results)
        
        # グラフ表示など
        st.line_chart(df_results[['ideal_width', 'ideal_height']])

if __name__ == "__main__":
    main()
