import config
import requests
import random

URL = "http://webservice.recruit.co.jp/hotpepper/gourmet/v1/"
response = requests.get(URL)
API_KEY = config.API_KEY

body = {
    'key':API_KEY,
    'keyword':'カレー店',
    'format':'json',
    'count':15,
    # 'lat':''
    # 'lng':''
}

response = requests.get(URL,body)
datum = response.json()
stores = datum['results']['shop']
select_shop = random.sample(stores, 10)
for store_info in select_shop:
    genre = store_info['genre']['name']
    name = store_info['name']
    print(genre, name)
