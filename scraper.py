import time
import re
from datetime import datetime # 👈 오늘 날짜 비교를 위해 필수 추가
from selenium import webdriver
from selenium.webdriver.common.by import By

def zenkaku_to_hankaku(text):
    if not text: return ""
    zenkaku_chars = "０１２３４５６７８９ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ：，（）"
    hankaku_chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz:,()"
    table = str.maketrans(zenkaku_chars, hankaku_chars)
    return text.translate(table).replace(" ", " ")

def clean_stock_name(name):
    if not name: return ""
    name = name.strip()
    while name.startswith("株式会社") or name.endswith("株式会社"):
        if name.startswith("株式会社"): name = name[4:].strip()
        if name.endswith("株式会社"): name = name[:-4].strip()
    return name

def parse_detail_page(driver, url):
    """상세 페이지 내부를 긁어오는 로직 (안전한 변수 초기화 포함)"""
    try:
        driver.get(url)
        time.sleep(2) # 상세 페이지 안정화 대기
        
        # 1. 요소를 먼저 찾습니다.
        content = driver.find_element(By.ID, "main-area")
        
        # 2. 요소를 찾은 후에 텍스트를 처리합니다.
        # [핵심] re.sub 호출 시 content.text를 사용하도록 순서 변경
        raw_text = content.text
        clean_text = re.sub(r'[^  \n]*に指定しました。', '', raw_text) 
        all_lines = [line.strip() for line in clean_text.split("\n") if line.strip()]

        # 3. 데이터 파싱 로직
        target_data = {
            "stock_name": "미검출", "stock_code": "미검출", "market_type": "미검출",
            "delisting_date": "미검출", "cleanup_start_date": "미검출", "cleanup_end_date": "미검출",
            "news_url": url
        }
        
        for line in all_lines:
            if line.startswith("（注）") or line.startswith("(注)"): continue
            
            if "銘柄" in line and "株式会社" in line:
                name_part = line.split("銘柄")[-1].strip()
                if name_part.endswith("株式"): name_part = name_part[:-2].strip()
                target_data["stock_name"] = clean_stock_name(zenkaku_to_hankaku(name_part))
            elif "コード" in line or "市場区分" in line:
                clean_line = zenkaku_to_hankaku(line)
                code_match = re.search(r"コード\s*[:：]\s*(\d+)", clean_line)
                if code_match: target_data["stock_code"] = code_match.group(1).strip()
                market_match = re.search(r"市場区分\s*[:：]\s*([^),，\s]+)", clean_line)
                if market_match: target_data["market_type"] = market_match.group(1).strip()
            elif "整理銘柄指定期間" in line and ("２" in line or "2" in line):
                period_part = zenkaku_to_hankaku(line.split("整理銘柄指定期間")[-1].strip())
                if "부터" in period_part or "から" in period_part:
                    raw_dates = re.split(r"부터|から", period_part)
                    target_data["cleanup_start_date"] = raw_dates[0].strip()
                    target_data["cleanup_end_date"] = raw_dates[1].replace("까지", "").replace("まで", "").strip()
            elif "上場廃止日" in line or ("３" in line or "3" in line) and "上場廃止日" in line:
                date_part = line.split("上場廃止日")[-1].strip()
                target_data["delisting_date"] = zenkaku_to_hankaku(date_part)

        return target_data

    except Exception as e:
        print(f"🚨 상세 페이지 파싱 중 에러 발생 ({url}): {e}")
        return None # 에러 시 None을 반환하여 메인 루프에서 건너뛰게 함

def run_scraper():
    print("--- [디버그] 크롤링 함수 진입! ---")
    
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--headless=new") 
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/125.0.0.0")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Remote(
        command_executor="http://localhost:4444/wd/hub", options=options
    )

    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.set_page_load_timeout(20)
    driver.implicitly_wait(10)

    results = []
    try:
        driver.get("https://www.jpx.co.jp/")
        time.sleep(2)
        driver.get("https://www.jpx.co.jp/news/index.html")
        time.sleep(3)

        # 💡 [핵심] 오늘 날짜를 다양한 형식으로 생성
        now = datetime.now()
        date_patterns = [
            now.strftime("%Y/%m/%d"),     # 2026/05/20
            now.strftime("%Y.%m.%d"),     # 2026.05.20
            f"{now.year}年{now.month}月{now.day}日" # 2026年5月20日
        ]
        
        print(f"디버깅: 오늘 날짜 검색어 후보: {date_patterns}")
        
        # 공시 리스트 전체를 가져와서 텍스트와 함께 로그 출력 (왜 못 찾는지 확인용)
        all_elements = driver.find_elements(By.XPATH, "//a[contains(., '上場廃止等の決定')]")
        
        unique_urls = set()
        for el in all_elements:
            url = el.get_attribute("href")
            text = el.text
            # 💡 [개선] 오늘 날짜 패턴 중 하나라도 포함되어 있는지 확인
            is_today = any(pattern in text for pattern in date_patterns)
            
            if url and is_today:
                unique_urls.add(url)
            
            # 로그 출력: 무엇을 찾았고 왜 오늘로 인식/비인식했는지 확인
            print(f"디버깅: 찾은 링크 텍스트: {text} | 오늘 날짜 포함 여부: {is_today}")
        
        print(f"디버깅: 오늘 수집된 타겟 URL 개수: {len(unique_urls)}")

        for target_url in unique_urls:
            try:
                detail_data = parse_detail_page(driver, target_url)
                if detail_data: # 데이터가 None이 아닐 때만 결과 리스트에 추가
                    results.append(detail_data)
            except Exception as detail_err:
                print(f"🚨 상세 페이지 파싱 에러: {detail_err}")
                continue

        return results

    finally:
        driver.quit()