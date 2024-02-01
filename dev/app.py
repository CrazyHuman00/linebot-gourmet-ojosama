# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
app.py : 近くの飲食店を検索してくれるお嬢様LINEBot
"""

__author__ = 'Hiroto Asakura'
__version__ = '3.11.6'
__date__ = '2024/2/2'

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

search_words = ["お腹すいた", "おなかすいた", "お腹空いた", "店検索", "ご飯たべたい", "お店", "ご飯"]


# テスト用
@app.route("/")
def test() -> str:
    """
    応答テスト

    Returns:
        str : "TEST OK"
    """
    return "TEST OK"


# 関数の呼び出し処理
@app.route("/callback")
def callback() -> str:
    """
    コールバック関数

    Returns:
        str : ステータスコード"OK"
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


def search_foodshop(address_name, keyword):
    """
    APIを使って飲食店検索する

    Args:
        keyword: キーワード
        address_name: 住所

    Returns:
        stores (str): 店情報
    """

    url = "https://webservice.recruit.co.jp/hotpepper/gourmet/v1/"

    api_key = info_config["API_KEY"]

    elements = {
        'key': api_key,
        'keyword': keyword,
        'address': address_name,
        'format': 'json',
        'count': 30
    }

    response = requests.get(url, elements)
    datum = response.json()

    try:
        stores = datum['results']['shop']
    except KeyError:
        print("Error: Unable to retrieve shop information from the response.")
        return []
    return random.sample(stores, 3)


# メッセージをやり取りする処理
@HANDLER.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.message.text in search_words:
        # キーワード
        LINE_BOT_API.reply_message(
            event.reply_token,
            TextSendMessage(text="何が食べたいですの？")
        )
        keyword = event.message.text

        # アドレス
        LINE_BOT_API.reply_message(
            event.reply_token,
            TextSendMessage(text="どの辺で食べたいですの？")
        )
        address_name = event.message.text

        # 検索
        stores = search_foodshop(address_name, keyword)

        # 店がなかった時の処理
        if stores is None:
            LINE_BOT_API.reply_message(
                event.reply_token,
                TextSendMessage(text="申し訳ございませんわ"
                                     "近くに飲食店がなかったみたいですの")
            )
            return

        # 応答メッセージ
        LINE_BOT_API.reply_message(
            event.reply_token,
            TextSendMessage(text=f"{keyword}で探した結果、このような店が見つかりましたわ")
        )

        for store in stores:
            shop_name: object = store['name']
            access = store['mobile_access']
            url = store['urls']

            LINE_BOT_API.reply_message(
                event.reply_token,
                TextSendMessage(text=f"{shop_name}{url}"
                                     f"{access}ですの")
            )

    else:
        LINE_BOT_API.reply_message(
            event.reply_token,
            TextSendMessage(text="お腹空きましたわねぇ")
        )


if "__main__" == __name__:
    import os

    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
