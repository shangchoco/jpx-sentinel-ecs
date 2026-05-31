import pymysql
import pymysql.cursors

def init_db():
    """
    SSHトンネル経由（localhost:3306）でRDSに接続し、DBおよびテーブルを初期化する。
    """
    print("🚀 DB初期化プロセスを開始します...")
    
    # SSHトンネルを経由するため、ホストは 127.0.0.1 を指定
    conn = pymysql.connect(
        host='127.0.0.1',
        user='admin',
        password='Password123!',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    
    try:
        with conn.cursor() as cursor:
            # 1. データベースの作成
            cursor.execute("""
                CREATE DATABASE IF NOT EXISTS jpx_database 
                CHARACTER SET utf8mb4 
                COLLATE utf8mb4_unicode_ci;
            """)
            cursor.execute("USE jpx_database;")
            
            # 2. テーブルの作成
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS delisting_news (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    stock_code VARCHAR(20),
                    stock_name VARCHAR(100),
                    market_type VARCHAR(50),
                    delisting_date VARCHAR(50),
                    cleanup_start_date VARCHAR(50),
                    cleanup_end_date VARCHAR(50),
                    news_url VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE KEY unique_stock (stock_code, delisting_date) -- 重複登録防止の制約
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            """)
        conn.commit()
        print("💡 [成功] データベースおよびテーブルの初期化が完了しました！")
    except Exception as e:
        print(f"❌ DB初期化中にエラーが発生しました: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()