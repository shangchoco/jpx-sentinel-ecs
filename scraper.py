import time
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By

def zenkaku_to_hankaku(text):
    """全角文字を半角に変換するユーティリティ"""
    if not text: return ""
    zenkaku_chars = "０１２３４５６７８９ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ：，（）"
    hankaku_chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz:,()"
    table = str.maketrans(zenkaku_chars, hankaku_chars)
    return text.translate(table).replace(" ", " ")

def clean_stock_name(name):
    """会社名から「株式会社」等の不要な接尾辞を除去する"""
    if not name: return ""
    name = name.strip()
    while name.startswith("株式会社") or name.endswith("株式会社"):
        if name.startswith("株式会社"): name = name[4:].strip()
        if name.endswith("株式会社"): name = name[:-4].strip()
    return name

def parse_detail_page(driver, url):
    """詳細ページから必要な情報を抽出するロジック"""
    try:
        driver.get(url)
        time.sleep(2) # ページの安定化待ち
        
        # main-areaからテキストを取得し、正規表現でクレンジング
        content = driver.find_element(By.ID, "main-area")
        raw_text = content.text
        clean_text = re.sub(r'[^  \n]*に指定しました。', '', raw_text) 
        all_lines = [line.strip() for line in clean_text.split("\n") if line.strip()]

        # 抽出したデータを格納する辞書
        target_data = {
            "stock_name": "未検出", "stock_code": "未検出", "market_type": "未検出",
            "delisting_date": "未検出", "cleanup_start_date": "未検出", "cleanup_end_date": "未検出",
            "news_url": url
        }
        
        for line in all_lines:
            if line.startswith("（注）") or line.startswith("(注)"): continue
            
            # 銘柄名抽出
            if "銘柄" in line and "株式会社" in line:
                name_part = line.split("銘柄")[-1].strip()
                if name_part.endswith("株式"): name_part = name_part[:-2].strip()
                target_data["stock_name"] = clean_stock_name(zenkaku_to_hankaku(name_part))
            # コードおよび市場区分抽出
            elif "コード" in line or "市場区分" in line:
                clean_line = zenkaku_to_hankaku(line)
                code_match = re.search(r"コード\s*[:：]\s*(\d+)", clean_line)
                if code_match: target_data["stock_code"] = code_match.group(1).strip()
                market_match = re.search(r"市場区分\s*[:：]\s*([^),，\s]+)", clean_line)
                if market_match: target_data["market_type"] = market_match.group(1).strip()
            # 整理銘柄指定期間抽出
            elif "整理銘柄指定期間" in line and ("２" in line or "2" in line):
                period_part = zenkaku_to_hankaku(line.split("整理銘柄指定期間")[-1].strip())
                if "부터" in period_part or "から" in period_part:
                    raw_dates = re.split(r"부터|から", period_part)
                    target_data["cleanup_start_date"] = raw_dates[0].strip()
                    target_data["cleanup_end_date"] = raw_dates[1].replace("まで", "").strip()
            # 上場廃止日抽出
            elif "上場廃止日" in line or ("３" in line or "3" in line) and "上場廃止日" in line:
                date_part = line.split("上場廃止日")[-1].strip()
                target_data["delisting_date"] = zenkaku_to_hankaku(date_part)

        return target_data

    except Exception as e:
        print(f"🚨 詳細ページ解析エラー ({url}): {e}")
        return None

def run_scraper():
    """JPXニュースサイトからデータをスクレイピングするメイン関数"""
    print("--- [デバッグ] スクレイピング関数開始 ---")
    
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--headless=new") 
    options.add_argument("user-agent=Mozilla/5.0...")
    
    driver = webdriver.Remote(command_executor="http://localhost:4444/wd/hub", options=options)

    try:
        driver.get("https://www.jpx.co.jp/news/index.html")
        time.sleep(3)

        # 本日の日付パターンを作成
        now = datetime.now()
        date_patterns = [
            now.strftime("%Y/%m/%d"), 
            now.strftime("%Y.%m.%d"), 
            f"{now.year}年{now.month}月{now.day}日"
        ]
        
        # 対象リンクを特定
        all_elements = driver.find_elements(By.XPATH, "//a[contains(., '上場廃止等の決定')]")
        unique_urls = set()
        
        for el in all_elements:
            url = el.get_attribute("href")
            text = el.text
            is_today = any(pattern in text for pattern in date_patterns)
            
            if url and is_today:
                unique_urls.add(url)
            print(f"デバッグ: リンクテキスト: {text} | 本日の日付判定: {is_today}")
        
        results = []
        for target_url in unique_urls:
            detail_data = parse_detail_page(driver, target_url)
            if detail_data: results.append(detail_data)

        return results

    finally:
        driver.quit()