# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
app.py : 近くのカレー店を検索してくれるお嬢様LINEBot
"""

__author__ = 'Hiroto Asakura'
__version__ = '3.9.15'
__date__ = '2023/12/1'

import json
import random
import requests

from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    CarouselColumn, CarouselTemplate, FollowEvent,
    LocationMessage, MessageEvent, TemplateSendMessage,
    TextMessage, TextSendMessage, UnfollowEvent, URITemplateAction
)

app = Flask(__name__)

# response.jsonから情報を取得
with open("./json/response.json", "r", encoding="utf8") as file:
    info_response = json.load(file)

# config.jsonから情報を取得
with open("./json/config.json", "r", encoding="utf8") as file:
    info_config = json.load(file)

LINE_BOT_API = LineBotApi(info_config["LINE_CHANNEL_ACCESS_TOKEN"])

HANDLER = WebhookHandler(info_config["LINE_CHANNEL_SECRET"])

NO_HIT_MESSAGE = info_response["NO_HIT_MESSAGE"]


# テスト用
@app.route("/")
def test() -> str:
    """
    応答テスト

    Returns:
        str : テストOK
    """
    return "TEST OK"


# 関数の呼び出し処理
@app.route("/callback")
def callback() -> str:
    """
    コールバック関数

    Returns:
        str : ステータスコード
    """

    # X-Line-Signature header valueを取得
    signature = request.headers['X-Line-Signature']

    # bodyを取得
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        HANDLER.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return "OK"


def search_curry(latitude, longitude, address_name):
    """
    APIを使ってカラー店を元に緯度経度を取得する

    Args:
        address_name:
        latitude (_type_): 緯度
        longitude (_type_): 経度

    Returns:
        _type_: _description_
    """

    url = "https://webservice.recruit.co.jp/hotpepper/gourmet/v1/"

    api_key = info_config["API_KEY"]

    elements = {
        'key': api_key,
        'keyword': 'カレー',
        'address': '京都府',
        'format': 'json',
        'lat': latitude,
        'lng': longitude
    }

    response = requests.get(url, elements)
    datum = response.json()

    try:
        stores = datum['results']['shop']['mobile_access']
    except KeyError:
        print("Error: Unable to retrieve shop information from the response.")
        return []
    return stores


# メッセージをやり取りする処理
@HANDLER.add(MessageEvent, message=LocationMessage)
def handle_location_message(event):
    user_latitude = event.message.latitude
    user_longitude = event.message.longitude
    address_name = event.message.text
    stores = search_curry(user_latitude, user_longitude, address_name)
    LINE_BOT_API.reply_message(
        event.reply_token,
        TextSendMessage(text="このような店が見つかりましたわ。")

    )


if "__main__" == __name__:
    import os

    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
