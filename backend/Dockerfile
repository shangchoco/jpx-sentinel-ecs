# [実行専用環境]
# ローカルでビルドされたJARファイルを実行するための軽量なJRE環境
FROM eclipse-temurin:17-jre-alpine

# コンテナ内部の作業ディレクトリを /app に設定
WORKDIR /app

# [重要] ビルド済みのJARファイルをコンテナ内部へコピー
# ローカルパス: build/libs/backend-0.0.1-SNAPSHOT.jar
# コンテナパス: /app/app.jar
COPY backend/build/libs/backend-0.0.1-SNAPSHOT.jar app.jar

# コンテナが外部に公開するポート番号
EXPOSE 8080

# アプリケーションの実行コマンド
ENTRYPOINT ["java", "-jar", "app.jar"]