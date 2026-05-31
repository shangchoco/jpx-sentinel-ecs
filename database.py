import os
import sys
import time
import pymysql
import pymysql.cursors

def get_db_connection(include_db=True):
    """
    MySQL接続オブジェクトを返却する。
    DB起動待ちのための再試行（リトライ）ロジックを含む。
    """
    max_retries = 10     # 最大リトライ回数
    retry_interval = 2   # リトライ間隔（秒）

    # 環境変数から接続情報を取得（運用環境への対応）
    rds_host = os.environ.get('DB_HOST')
    db_user = os.environ.get('DB_USER')
    db_password = os.environ.get('DB_PASSWORD')
    db_name = os.environ.get('DB_NAME')

    # 必須環境変数のチェック
    if not all([rds_host, db_user, db_password, db_name]):
        print("エラー: 必須環境変数(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)が設定されていません。")
        sys.exit(1)
    
    for attempt in range(max_retries):
        try:
            conn = pymysql.connect(
                host=rds_host,
                user=db_user,
                password=db_password,
                database=db_name if include_db else None,
                charset='utf8mb4',  # 日本語文字化け防止用設定
                cursorclass=pymysql.cursors.DictCursor
            )
            return conn
            
        except pymysql.err.OperationalError as e:
            # まだDBが準備できていない場合（Connection refused等）
            if attempt < max_retries - 1:
                print(f"⏳ [待機] DBサーバー準備中... ({attempt + 1}/{max_retries}) {retry_interval}秒後に再試行します。")
                time.sleep(retry_interval)
            else:
                print("❌ [失敗] DB接続の最大リトライ回数を超えました。")
                raise e

def init_db():
    """
    アプリケーション起動時にDBおよびテーブルを自動初期化・生成する。
    """
    # 1. データベースが存在しない場合は作成
    conn = get_db_connection(include_db=False)
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE DATABASE IF NOT EXISTS jpx_database 
                CHARACTER SET utf8mb4 
                COLLATE utf8mb4_unicode_ci;
            """)
        conn.commit()
    finally:
        conn.close()

    # 2. テーブル生成（ニュースURLカラムを追加）
    conn = get_db_connection(include_db=True)
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS delisting_news (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    stock_code VARCHAR(20),
                    stock_name VARCHAR(100),
                    market_type VARCHAR(50),
                    delisting_date VARCHAR(50),
                    cleanup_start_date VARCHAR(50),
                    cleanup_end_date VARCHAR(50),
                    news_url VARCHAR(255), -- 公式発表リンク用カラム
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE KEY unique_stock (stock_code, delisting_date) -- 重複防止制約
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            """)
        conn.commit()
        print("💡 [成功] データベースおよびテーブルの初期化完了！")
    except Exception as e:
        print(f"❌ DB初期化中にエラー発生: {e}")
    finally:
        conn.close()

def save_to_db(data):
    """
    スクレイピングデータをDBに保存する。
    新規データならTrue、重複等の理由で保存されなければFalseを返却。
    """
    
    # [防御ロジック] 不正なデータ（上場廃止関連の注釈等）のフィルタリング
    if any(keyword in data.get('stock_name', '') for keyword in ["指定しました", "上場廃止"]):
        print(f"❌ [汚染データ遮断] stock_code: {data.get('stock_code')} - 保存処理をスキップ")
        return False

    conn = get_db_connection(include_db=True)
    try:
        with conn.cursor() as cursor:
            sql = """
                INSERT IGNORE INTO delisting_news 
                (stock_code, stock_name, market_type, delisting_date, cleanup_start_date, cleanup_end_date, news_url) 
                VALUES (%s, %s, %s, %s, %s, %s, %s);
            """
            cursor.execute(sql, (
                data.get('stock_code'),
                data.get('stock_name'),
                data.get('market_type'),
                data.get('delisting_date'),
                data.get('cleanup_start_date'),
                data.get('cleanup_end_date'),
                data.get('news_url')
            ))
            conn.commit()
            
            # 実際に挿入された行が1であれば新規データ（True）、重複していれば0（False）
            return cursor.rowcount > 0 
            
    except Exception as e:
        print(f"❌ DB保存中にエラー発生: {e}")
        return False
    finally:
        conn.close()