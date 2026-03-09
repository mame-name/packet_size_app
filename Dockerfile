# 1. ベースイメージの指定 (軽量な slim 版がおすすめ)
FROM python:3.11-slim

# 2. コンテナ内の作業ディレクトリを設定
WORKDIR /app

# 3. 依存関係のインストールに必要なツールを入れる (念のため)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# 4. 依存関係ファイルをコピーしてインストール
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# 5. アプリケーションのソースコードをコピー
COPY . .

# 6. Streamlit がデフォルトで使用するポート 8501 を開放
EXPOSE 8501

# 7. 実行時のヘルスチェック（オプションですが推奨）
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# 8. アプリの起動コマンド
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
