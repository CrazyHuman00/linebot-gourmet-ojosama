# !/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Asakura Hiroto'
__version__ = '2.0.0'
__date__ = '2024/07/16 (Created: 2024/02/02)'

# ライブラリのインポート
from flask import Flask, request, abort
from linebot.models import (MessageEvent, TextMessage)
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)

# Flaskのインスタンス
app = Flask(__name__)

import json


# config.jsonから情報を取得
with open("./config.json", "r", encoding="utf8") as file:
    info_config = json.load(file)

LINE_BOT_API = LineBotApi(info_config["LINE_CHANNEL_ACCESS_TOKEN"])

HANDLER = WebhookHandler(info_config["LINE_CHANNEL_SECRET"])

SEARCH_WORD = ["お腹すいた"]

