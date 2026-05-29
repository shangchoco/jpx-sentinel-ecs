import os
import traceback
from flask import Flask, jsonify
from scraper import run_scraper
from database import init_db, save_to_db
from slack_alarm import send_slack_alarm

app = Flask(__name__)
app.json.ensure_ascii = False

# [운영 환경 제어] ECS 환경 변수에서 MODE를 읽어와 DB 초기화 여부를 결정합니다.
# PRODUCTION 모드에서는 DB 초기화를 건너뛰어 안정성을 확보합니다.
APP_MODE = os.environ.get("APP_MODE", "PRODUCTION")

print(f"--- [시스템] 서버 모드: {APP_MODE} ---")
print("--- [디버그] Flask 서버 실행 시도 중 ---")

if APP_MODE == "DEV":
    # 앱 구동 시 DB 테이블 자동 생성
    print("--- [디버그] 개발 모드: DB 테이블 자동 생성 시도 ---")
    init_db()
    print("--- [디버그] DB 초기화 완료, 라우트 정의 시작 ---")
else:
    print("--- [시스템] 운영 모드: DB 초기화 과정을 생략합니다. ---")

def process_and_alarm(item):
    """
    개별 종목 데이터를 DB에 저장을 시도하고, 
    새로 저장된(신규) 데이터일 경우에만 슬랙 알림을 발송하는 헬퍼 함수
    """
    if not isinstance(item, dict):
        return False

    # 1. DB 저장 시도 (save_to_db가 신규 저장 성공 시 True, 중복 무시 시 False를 리턴한다고 가정)
    is_new_inserted = save_to_db(item)
    
    # 2. 💡 오직 신규로 등록된 데이터일 때만 슬랙 알림 트리거 (중복 데이터면 알림 안 감)
    if is_new_inserted:
        news_link = item.get('news_url')
        code = item.get('stock_code', '0000')
        
        if not news_link:
            news_link = f"https://www.jpx.co.jp/listing/stocks/show?code={code}"

        send_slack_alarm(
            stock_name=item.get('stock_name', '이름 없음'),
            stock_code=code,    
            delisting_date=item.get('delisting_date', '날짜 정보 없음'),
            link=news_link
        )
        return True # 신규 등록 성공 표시
        
    return False # 중복 데이터였음

@app.route("/", methods=["GET"])
def health_check():
    return "OK", 200

@app.route("/python/scrape", methods=["GET"])
def trigger_scraper():

    print("--------------------------------------------------")
    print(">>> [디버그] /scrape 라우트 진입 성공! <<<")
    print("--------------------------------------------------")
    
    try:
        # 이 부분이 실행되는지 확인
        print(">>> [디버그] /scrape 라우트 호출됨!", flush=True) # 이것도 찍히는지 확인
        result_data = run_scraper()
        print(f">>> [디버그] run_scraper 완료, 결과: {result_data}")

        # 2. 결과값이 None일 경우 빈 리스트로 초기화 (에러 방지)
        if result_data is None:
            result_data = []

        new_inserted_count = 0
        
        # 3. 데이터가 리스트인지 확인하고 순회
        if isinstance(result_data, list):
            for item in result_data:
                if process_and_alarm(item):
                    new_inserted_count += 1
        elif isinstance(result_data, dict):
            if process_and_alarm(result_data):
                new_inserted_count += 1
        elif isinstance(result_data, str):
            send_slack_alarm(result_data, "정보 없음", "정보 없음", link=None)

        # 4. 응답 구성 시 len() 안전하게 호출
        total_scraped = len(result_data) if isinstance(result_data, list) else 1
        
        return jsonify({
            "status": "success",
            "message": f"오늘 자 신규 공시 {new_inserted_count}건 등록.",
            "total_scraped": total_scraped,
            "new_inserted": new_inserted_count
        })
        
    except Exception as e:
        # 5. [핵심] 500 에러 발생 시 상세 에러 내용을 터미널에 무조건 출력
        print("🚨🚨 상세 에러 발생 🚨🚨")
        traceback.print_exc()  # 에러 위치와 원인을 아주 상세히 출력함
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    # 포트 8080은 root 권한이 필요하므로, ECS 환경에 맞게 8080으로 설정했습니다.
    app.run(host="0.0.0.0", port=8080, debug=False)