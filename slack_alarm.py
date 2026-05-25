import requests

def send_slack_alarm(stock_name, stock_code, delisting_date, link=None):
    # 💡 본인의 Webhook URL
    webhook_url = "PLACEHOLDER_FOR_SLACK_WEBHOOK"
    
    # 링크가 있을 경우 필드에 추가하거나 텍스트에 포함
    # 여기서는 상장폐지 예정일 아래에 깔끔하게 배치.
    actions = []
    if link:
        actions = [
            {
                "type": "button",
                "text": "🔗 JPX 상세 페이지 이동",
                "url": link,
                "style": "primary" # 파란색 버튼
            }
        ]

    payload = {
        "text": "🚨 *상장폐지 신규 종목 발견*",
        "attachments": [
            {
                "color": "#EB4646",  # 강렬한 빨간색
                "fields": [
                    {"title": "종목명", "value": stock_name, "short": True},
                    {"title": "종목코드", "value": stock_code, "short": True},
                    {"title": "상장폐지 예정일", "value": delisting_date, "short": False}
                ],
                "actions": actions, # 💡 버튼 형식으로 링크 추가
                "footer": "JPX Monitoring System",
                "footer_icon": "https://a.slack-edge.com/80588/img/services/incoming-webhook_512.png"
            }
        ]
    }

    try:
        response = requests.post(webhook_url, json=payload)
        print(f"슬랙 응답 상태 코드: {response.status_code}") 
        return response.status_code == 200
    except Exception as e:
        print(f"Slack 전송 에러: {e}")
        return False