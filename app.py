# !/bin/bash
# -*- coding: utf-8 -*-
"""
app.py : 近くのカレー店を検索してくれるお嬢様LINEBot
"""

import config
from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

app = Flask(__name__)

line_bot_api = LineBotApi(config.LINE_CHANNEL_ACCESS_TOKEN)  # config.pyで設定したチャネルアクセストークン
handler = WebhookHandler(config.LINE_CHANNEL_SECRET)         # config.pyで設定したチャネルシークレット


@app.route("/")
def test():
    """
    応答テスト

    Returns:
        str : テストOK
    """
    return "TEST OK"

@app.route("/callback")
def callback():
    """
    コールバック関数

    Returns:
        str : 繋がったかどうかをOKで示してくれる
    """
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

