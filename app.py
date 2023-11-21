# !/bin/bash
# -*- coding: utf-8 -*-

"""
app.py : 近くのカレー店を検索してくれるお嬢様LINEBot
"""

import config     # config.pyのインポート

import requests
import urllib.parse
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

line_bot_api = LineBotApi(config.LINE_CHANNEL_ACCESS_TOKEN)  # config.pyで設定したチャネルアクセストークン
handler = WebhookHandler(config.LINE_CHANNEL_SECRET)         # config.pyで設定したチャネルシークレット

no_hit_message = "近くにカレー屋さんはないようです"
not_found_message = """
申し訳ありません、データを取得できませんでした。
少し時間を空けて、もう一度試してみてください。
"""
DAMMY_URL = "https://canbus.com/blog/wp-content/uploads/2018/02/2015-tenpo.jpg"


# テスト用
@app.route("/")
def test():
    """ 応答テスト

    Returns:
        str : テストOK
    """
    return "TEST OK"


# 関数の呼び出し処理
@app.route("/callback")
# コールバック関数
def callback():
    """ コールバック関数

    Returns:
        str : ステータスコード
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


# ホットペッパーAPIを使って検索
def search_rest(latitude, longitude):
    """ APIからカレーをもとに緯度経度を取得する

    Args:
        latitude (_type_): _description_
        longitude (_type_): _description_

    Raises:
        Exception: _description_
        Exception: _description_
        Exception: _description_

    Returns:
        _type_: _description_
    """
    url = "https://webservice.recruit.co.jp/hotpepper/shop/v1/"
    params = {}
    params['latitude'] = latitude
    params['longitude'] = longitude
    params['range'] = 3
    params['genre'] = "カレー"
    response = requests.get(url, params)
    results = response.json()
    if "error" in results:
        if "message" in results:
            raise Exception("{}".format(results["message"]))
        else:
            raise Exception(not_found_message)
    total_hit_count = results.get("total_hit_count", 0)
    if total_hit_count < 1:
        raise Exception(no_hit_message)
    return results


#
