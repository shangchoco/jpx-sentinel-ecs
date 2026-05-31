# 1. ベースイメージに軽量なPython環境を指定
FROM python:3.13-slim

# 2. コンテナ内の作業ディレクトリを設定
WORKDIR /app

# 3. 依存ライブラリ一覧をコピーし、パッケージをインストール
# キャッシュを無効化してイメージサイズを最適化
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. ローカルのソースコードをコンテナ内の作業ディレクトリへコピー
COPY . .

# 5. コンテナが外部に公開するポート番号
EXPOSE 80

# 6. コンテナ起動時に実行するコマンド
CMD ["python", "main.py"]