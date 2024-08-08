# !/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Asakura'
__version__ = '2.0.0'
__date__ = '2024/07/16 (Created: 2024/07/21)'

import os
import requests
import random

URL = 'http://webservice.recruit.co.jp/hotpepper/gourmet/v1/'
API_KEY = os.environ.get("LINE_CHANNEL_SECRET")

def search_restaurant():
    a = 10

def trigger():
    body = {
    'key': API_KEY,
    'keyword': "中華",
    'format': 'json',
    'count': 100
    }