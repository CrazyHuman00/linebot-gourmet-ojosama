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
    MessageEvent, TextMessage, TextSendMessage
)

app = Flask(__name__)

# config.jsonから情報を取得
with open("./json/config.json", "r", encoding="utf8") as file:
    info_config = json.load(file)

LINE_BOT_API = LineBotApi(info_config["LINE_CHANNEL_ACCESS_TOKEN"])

HANDLER = WebhookHandler(info_config["LINE_CHANNEL_SECRET"])

SEARCH_WORD = ["お腹すいた", "おなかすいた", "お腹空いた", "店検索", "ご飯たべたい", "お店", "ご飯"]

sessions = {"hungry": False, "where": False, "keyword": None, "city_name": None}


# 関数の呼び出し処理
@app.route("/callback", methods=['POST'])
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


def search_foodshop(keyword, city_name):
    """
    APIを使って飲食店検索する

    Args:
        keyword (str): キーワード
        city_name (str): 都市名
    Returns:
        shops (str): 店情報
    """

    url = "https://webservice.recruit.co.jp/hotpepper/gourmet/v1/"

    api_key = info_config["API_KEY"]

    elements = {
        'key': api_key,
        'keyword': keyword,
        'address': city_name,
        'format': 'json',
        'count': 10
    }

    response = requests.get(url, elements)
    datum = response.json()

    try:
        shops = datum['results']['shop']
        random_shops = random.sample(shops, 3)
        return random_shops
    except KeyError:
        print("Error: Unable to retrieve shop information from the response.")
        return []


# メッセージをやり取りする処理
@HANDLER.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global sessions

    if not event.source.user_id in sessions.keys():
        sessions[event.source.user_id] = {"hungry_flag": False, "where_flag": False,
                                          "keyword": None, "city_name": None}

    if event.message.text in SEARCH_WORD:
        sessions[event.source.user_id]["hungry_flag"] = True
        LINE_BOT_API.reply_message(
            event.reply_token,
            TextSendMessage(text="何が食べたいですの？")
        )

    elif event.message.text == "ありがとう":
        LINE_BOT_API.reply_message(
            event.reply_token,
            TextSendMessage(
                text="どういたしましてですの♪"
            )
        )

    elif sessions[event.source.user_id]["hungry_flag"]:
        sessions[event.source.user_id]["keyword"] = event.message.text
        sessions[event.source.user_id]["where_flag"] = True
        sessions[event.source.user_id]["hungry_flag"] = False
        LINE_BOT_API.reply_message(
            event.reply_token,
            TextSendMessage(text="どの辺で食べたいですの？")
        )

    elif sessions[event.source.user_id]["where_flag"]:
        sessions[event.source.user_id]["city_name"] = event.message.text

        shops = search_foodshop(sessions[event.source.user_id]["keyword"],
                                sessions[event.source.user_id]["city_name"])

        columns = []
        if shops is None:
            LINE_BOT_API.reply_message(
                event.reply_token,
                TextSendMessage(text="申し訳ございませんわ"
                                     "近くに飲食店がなかったみたいですの")
            )
            return

        for shop_info in shops:
            shop_name = shop_info.get('name')
            access = shop_info.get('mobile_access')
            url = shop_info.get('urls').get('pc')
            polite_ending = ["ます。", "です。"]
            if access[:-3] in polite_ending:
                access = access[:-3]
            columns.append([shop_name, access, url])

        result_message = ""
        for shop_name, access, url in columns:
            reply_text = f"このような店が見つかりましたわ\n{shop_name}\n{url}\n{access}のところにありますの\n"
            result_message += reply_text + "\n"

        LINE_BOT_API.reply_message(
            event.reply_token,
            TextSendMessage(
                text=result_message
            )
        )

    else:
        LINE_BOT_API.reply_message(
            event.reply_token,
            TextSendMessage(text="お腹空きましたわねぇ")
        )


# TODO: 位置情報からでも検索できる機能の作成

if __name__ == "__main__":
    app.run(host="localhost", port=8000)
