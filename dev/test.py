import requests
import random

URL = "https://webservice.recruit.co.jp/hotpepper/gourmet/v1/"
response = requests.get(URL)
API_KEY = "a902d5426ee72db7"

body = {
    'key': API_KEY,
    'keyword': 'カレー',
    'address': '京都府',
    'format': 'json',
    'count': 30,
}


def get_selected_shops(url, elements, num_shops=10):
    response = requests.get(url, elements)
    datum = response.json()

    try:
        stores = datum['results']['shop']
    except KeyError:
        print("Error: Unable to retrieve shop information from the response.")
        return []

    return stores


# ジャンル、店名、アクセスを表示する
def print_shop_info(shop_info):
    genre = shop_info['genre']['name']
    address = shop_info['address']
    name = shop_info['name']
    lat = shop_info['lat']
    lng = shop_info['lng']
    url = shop_info['urls']
    access = shop_info['mobile_access']
    print(f"{genre} - {name} - {access} - {url}")



def main():
    selected_shops = get_selected_shops(URL, body)

    for store_info in selected_shops:
        print_shop_info(store_info)


if __name__ == "__main__":
    main()
