import os
import traceback
import sys
from flask import Flask, jsonify
from scraper import run_scraper
from database import init_db, save_to_db
from slack_alarm import send_slack_alarm

app = Flask(__name__)
app.json.ensure_ascii = False

# [運用環境制御] ECS環境変数からMODEを読み取り、DB初期化の可否を決定
# PRODUCTIONモードではDB初期化をスキップして安定性を確保
# BATCHモード追加: ECS起動時にクロール実行後、自動終了
APP_MODE = os.environ.get("APP_MODE", "BATCH")

print(f"--- [システム] サーバーモード: {APP_MODE} ---")

if APP_MODE == "DEV":
    # アプリ起動時にDBテーブルを自動生成
    print("--- [デバッグ] 開発モード: DBテーブル自動生成を試行 ---")
    init_db()
    print("--- [デバッグ] DB初期化完了、ルート定義開始 ---")
elif APP_MODE == "BATCH":
    print("--- [システム] BATCHモード: 直ちにクロールを実行し終了します。 ---")
else:
    # 運用モード等
    print("--- [システム] 運用モード: DB初期化プロセスをスキップします。 ---")

def process_and_alarm(item):
    """
    個別銘柄データのDB保存を試行し、新規データの場合のみSlack通知を送信するヘルパー関数
    """
    if not isinstance(item, dict):
        return False

    # 1. DB保存を試行 (新規保存成功時にTrue、重複時はFalseを返却)
    is_new_inserted = save_to_db(item)
    
    # 2. 新規登録データのみSlack通知をトリガー
    if is_new_inserted:
        news_link = item.get('news_url')
        code = item.get('stock_code', '0000')
        
        if not news_link:
            news_link = f"https://www.jpx.co.jp/listing/stocks/show?code={code}"

        send_slack_alarm(
            stock_name=item.get('stock_name', '名称不明'),
            stock_code=code,    
            delisting_date=item.get('delisting_date', '日付情報なし'),
            link=news_link
        )
        return True # 新規登録成功
        
    return False # 重複データ

@app.route("/", methods=["GET"])
def health_check():
    return "OK", 200

@app.route("/python/scrape", methods=["GET"])
def trigger_scraper():
    print("--------------------------------------------------")
    print(">>> [デバッグ] /scrape ルートへ進入成功！ <<<")
    print("--------------------------------------------------")
    
    try:
        print(">>> [デバッグ] /scrape ルート呼び出し！", flush=True)
        result_data = run_scraper()
        print(f">>> [デバッグ] run_scraper完了、結果: {result_data}")

        # 結果がNoneの場合は空リストで初期化（エラー回避）
        if result_data is None:
            result_data = []

        new_inserted_count = 0
        
        # データがリスト形式か確認して順次処理
        if isinstance(result_data, list):
            for item in result_data:
                if process_and_alarm(item):
                    new_inserted_count += 1
        elif isinstance(result_data, dict):
            if process_and_alarm(result_data):
                new_inserted_count += 1
        elif isinstance(result_data, str):
            send_slack_alarm(result_data, "情報なし", "情報なし", link=None)

        total_scraped = len(result_data) if isinstance(result_data, list) else 1
        
        return jsonify({
            "status": "success",
            "message": f"本日の新規公示 {new_inserted_count} 件登録。",
            "total_scraped": total_scraped,
            "new_inserted": new_inserted_count
        })
        
    except Exception as e:
        # [重要] 500エラー発生時の詳細エラー内容をターミナルに出力
        print("🚨🚨 詳細エラー発生 🚨🚨")
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

def run_batch_task():
    """バッチモードでクロール処理を実行し、プロセスを終了する関数"""
    try:
        result_data = run_scraper()
        if result_data is None: result_data = []
        
        new_inserted_count = 0
        if isinstance(result_data, list):
            for item in result_data:
                if process_and_alarm(item):
                    new_inserted_count += 1
        elif isinstance(result_data, dict):
            if process_and_alarm(result_data):
                new_inserted_count += 1
        
        print(f">>> [システム] バッチ作業完了: 新規 {new_inserted_count} 件登録。")
    except Exception as e:
        print("🚨🚨 バッチ作業中に詳細エラー発生 🚨🚨")
        traceback.print_exc()
        sys.exit(1) # エラー時終了コード 1
    
    sys.exit(0) # 成功時終了コード 0 (ECSコンテナ停止用)

if __name__ == "__main__":
    if APP_MODE == "BATCH":
        run_batch_task()
    else:
        # ECS環境に適したポート 8080 で実行
        app.run(host="0.0.0.0", port=8080, debug=False)