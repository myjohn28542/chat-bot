from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from django.http import JsonResponse
import requests
import os

LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

line_bot_api = LineBotApi(LINE_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

def line_webhook(request):
    if request.method == "POST":
        body = request.body.decode("utf-8")
        event = request.json["events"][0]
        user_id = event["source"]["userId"]
        message = event["message"]["text"]

        response = requests.post("http://127.0.0.1:8000/api/chat/", json={
            "user_id": user_id,
            "message": message,
            "platform": "LINE"
        })
        bot_reply = response.json()["response"]

        line_bot_api.reply_message(event["replyToken"], TextSendMessage(text=bot_reply))
        return JsonResponse({"status": "success"})

    return JsonResponse({"status": "error"})