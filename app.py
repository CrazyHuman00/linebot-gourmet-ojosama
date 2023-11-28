# !/bin/bash
# -*- coding: utf-8 -*-

"""
app.py : 近くのカレー店を検索してくれるお嬢様LINEBot
"""

import config                               # config.pyのインポート

import random                               # 乱数のインポート
import requests                             # requestsのインポート
from flask import Flask, request, abort     # Flaskのインポート
from linebot import (                       # linebotAPIのインポート
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (            # linebotAPIにおけるwebhookのインポート
    InvalidSignatureError
)
from linebot.models import (                # linebotのmodelsパッケージ
    CarouselColumn, CarouselTemplate, FollowEvent,
    LocationMessage, MessageEvent, TemplateSendMessage,
    TextMessage, TextSendMessage, UnfollowEvent, URITemplateAction
)

app = Flask(__name__)

line_bot_api = LineBotApi(config.LINE_CHANNEL_ACCESS_TOKEN) # config.pyで設定したチャネルアクセストークン
handler = WebhookHandler(config.LINE_CHANNEL_SECRET)        # config.pyで設定したチャネルシークレット

# メッセージ
no_hit_message = "近くにカレー屋さんはないようです"              # ヒットしなかった時のメッセージ
not_found_message = "申し訳ありません、データを取得できませんでした。少し時間を空けて、もう一度試してみてください。"                                                           # 見つからなかった時のメッセージ



# ホットペッパーAPI取得のための情報
URL = "http://webservice.recruit.co.jp/hotpepper/gourmet/v1/"  # リクエストURL
API_KEY = config.API_KEY                                       # APIKEY


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
def callback():
    """ コールバック関数

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
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


def search_rest(latitude, longitude):
    """ APIを使ってカラー店を元に緯度経度を取得する

    Args:
        latitude (_type_): _description_
        longitude (_type_): _description_


    Returns:
        _type_: _description_
    """

    # 検索クエリからbodyを作成(条件をここで絞る)
    body = {
        'key': API_KEY,
        'keyword': 'カレー店',
        'format': 'json',
        'count': 15,
        'lat': latitude,
        'lng': longitude
    }

    response = requests.get(URL, body)
    datum = response.json()
    stores = datum['results']['shop']
    select_shop = random.sample(stores, 10)
    for store_info in select_shop:
        genre = store_info['genre']['name']
        name = store_info['name']
        print(genre, name)




# メッセージをやり取りする処理
@handler.add(MessageEvent, message=LocationMessage)
def handle_location_message(event):
    a = 10
