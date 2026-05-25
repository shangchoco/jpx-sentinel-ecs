import time
import pymysql
import pymysql.cursors

def get_db_connection(include_db=True):
    """MySQL 연결을 반환합니다. (DB 부팅 대기용 재시도 로직 포함)"""
    max_retries = 10     # 최대 10번 재시도
    retry_interval = 2   # 2초 간격으로 시도 (총 20초 대기)
    
    for attempt in range(max_retries):
        try:
            conn = pymysql.connect(
                host='db',
                user='root',
                password='rootpassword',
                database='jpx_database' if include_db else None,
                charset='utf8mb4',  # 일본어 깨짐 방지 세팅
                cursorclass=pymysql.cursors.DictCursor
            )
            return conn  # 연결 성공 시 즉시 커넥션 반환
            
        except pymysql.err.OperationalError as e:
            # 아직 DB가 준비 안 된 경우 (Connection refused 등)
            if attempt < max_retries - 1:
                print(f"⏳ [대기] DB 서버가 준비 중입니다... ({attempt + 1}/{max_retries}) {retry_interval}초 후 다시 시도합니다.")
                time.sleep(retry_interval)
            else:
                print("❌ [실패] DB 연결 최대 재시도 횟수를 초과했습니다.")
                raise e

def init_db():
    """앱이 켜질 때 DB와 테이블을 자동으로 초기화하고 생성합니다."""
    # 1. 데이터베이스가 없으면 생성
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

    # 2. 테이블 생성 (💡 news_url 컬럼 추가)
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
                    news_url VARCHAR(255), -- 👈 [변경] 실제 공시 링크를 보관할 컬럼 추가
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE KEY unique_stock (stock_code, delisting_date) -- 중복 방지 제약조건
                ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
            """)
        conn.commit()
        print("💡 [성공] 깨짐방지용 데이터베이스 및 테이블 초기화 완료!")
    except Exception as e:
        print(f"❌ DB 초기화 중 에러 발생: {e}")
    finally:
        conn.close()

def save_to_db(data):
    """스크래핑한 데이터를 DB에 안전하게 저장하고, 신규 데이터면 True, 중복이면 False 반환"""
    
    # [방어 로직] 들여쓰기 확인! (함수 내부로 4칸 들어와야 합니다)
    if any(keyword in data.get('stock_name', '') for keyword in ["指定しました", "上場廃止"]):
        print(f"❌ [오염 데이터 차단] stock_code: {data.get('stock_code')} - 저장 시도 차단됨")
        return False

    conn = get_db_connection(include_db=True)
    try:
        with conn.cursor() as cursor:
            # 💡 news_url 컬럼과 매핑값(%s) 추가
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
                data.get('news_url') # 👈 [변경] 스크래퍼가 가져온 URL 매핑
            ))
            conn.commit()
            
            # 실제로 삽입된 행이 1개면 신규 데이터(True), 중복되어 무시되면 0이므로 (False) 반환
            return cursor.rowcount > 0 
            
    except Exception as e:
        print(f"❌ DB 저장 중 에러 발생: {e}")
        return False
    finally:
        conn.close()