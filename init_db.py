import pymysql
import pymysql.cursors

def init_db():
    """SSH 터널링(localhost:3306)을 통해 RDS에 DB와 테이블을 생성합니다."""
    print("🚀 DB 초기화 시작...")
    
    # 터널링을 통해 연결하므로 host는 127.0.0.1 입니다.
    conn = pymysql.connect(
        host='127.0.0.1',
        user='admin',
        password='Password123!',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    
    try:
        with conn.cursor() as cursor:
            # 1. 데이터베이스 생성
            cursor.execute("""
                CREATE DATABASE IF NOT EXISTS jpx_database 
                CHARACTER SET utf8mb4 
                COLLATE utf8mb4_unicode_ci;
            """)
            cursor.execute("USE jpx_database;")
            
            # 2. 테이블 생성
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
                    UNIQUE KEY unique_stock (stock_code, delisting_date)
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            """)
        conn.commit()
        print("💡 [성공] 깨짐방지용 데이터베이스 및 테이블 초기화 완료!")
    except Exception as e:
        print(f"❌ DB 초기화 중 에러 발생: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()