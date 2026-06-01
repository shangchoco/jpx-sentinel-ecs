import os
import requests

def send_slack_alarm(stock_name=None, stock_code=None, delisting_date=None, link=None, is_no_data=False):
    """
    JPX上場廃止情報をSlackに通知する。
    WebHook URLは環境変数より取得。
    is_no_dataがTrueの場合は、データなしの正常報告を通知。
    """
    # 💡 Slack Webhook URLは環境変数から取得
    webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
    
    # データがない場合の正常通知ペイロード
    if is_no_data:
        payload = {
            "text": "✅ *本日の上場廃止銘柄検知: なし*",
            "attachments": [
                {
                    "color": "#36a64f",  # 正常報告用の緑色
                    "text": "本日、新たに検出された上場廃止銘柄はありませんでした。システムは正常に稼働中です。",
                    "footer": "JPX Monitoring System"
                }
            ]
        }
    else:
        # リンクがある場合はボタンアクションとして追加
        actions = []
        if link:
            actions = [
                {
                    "type": "button",
                    "text": "🔗 JPX詳細ページへ移動",
                    "url": link,
                    "style": "primary" # 青色のボタン
                }
            ]

        # 通知ペイロードの設定
        payload = {
            "text": "🚨 *新規上場廃止銘柄を検知しました*",
            "attachments": [
                {
                    "color": "#EB4646",  # 強調用の赤色
                    "fields": [
                        {"title": "銘柄名", "value": stock_name, "short": True},
                        {"title": "証券コード", "value": stock_code, "short": True},
                        {"title": "上場廃止予定日", "value": delisting_date, "short": False}
                    ],
                    "actions": actions, # リンクボタン
                    "footer": "JPX Monitoring System",
                    "footer_icon": "https://a.slack-edge.com/80588/img/services/incoming-webhook_512.png"
                }
            ]
        }

    try:
        response = requests.post(webhook_url, json=payload)
        print(f"Slack通知ステータスコード: {response.status_code}") 
        return response.status_code == 200
    except Exception as e:
        print(f"Slack送信エラー: {e}")
        return False