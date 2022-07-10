from django.shortcuts import render
import requests
import json
import pprint
import time
import datetime

# Create your views here.


def index(request):
    prefectures_json = {'prefectures': []}
    with open('static/trip_maker/text/prefectures.txt') as file:
        if (not file):
            print('ファイルが読み込めませんでした')
        prefectures_json['prefectures'].append(file.readline)
    return render(request, 'trip_maker/index.html', prefectures_json)


def google_func(place_name):
    params = {
        "query": place_name + " 観光",
        "key": "AIzaSyA5SmbNJlpGTV_v6aAtKS-caYI8OpNFQGg",
        "region": "jp",
        "language": "ja",
    }

    google_api_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"

    res = requests.get(google_api_url, params=params)
    place = json.loads(res.text)

    # 受け取った都道府県から評価数が多い10個の場所を探す
    rating_total = []
    array = []
    location_lat = []
    location_lng = []
    name = []
    rating = []
    return_val = []

    for place in place["results"]:
        location_lat.append(place["geometry"]["location"]["lat"])
        location_lng.append(place["geometry"]["location"]["lng"])
        rating_total.append(place["user_ratings_total"])
        rating.append(place["rating"])
        name.append(place["name"])
        array.append(place["user_ratings_total"])

    array = sorted(array, reverse=True)
    for i in range(10):
        num = array[i]
        rating_index = rating_total.index(num)
        place_info = dict.fromkeys(
            ['name', 'lat', 'long', 'num_of_reviews', 'review_rating'])
        place_info['name'] = name[rating_index]
        place_info['lat'] = location_lat[rating_index]
        place_info['long'] = location_lng[rating_index]
        place_info['num_of_reviews'] = rating_total[rating_index]
        place_info['review_rating'] = rating[rating_index]
        return_val.append(place_info)
    return return_val


def main(request, room_name):
    spots_json = {'room_name': room_name, 'spots': []}
    # TODO　都道府県名から人気がある(口コミが多い)のスポットの
    # 上位10件を抽出。つまり、入力が都道府県名で戻り値がspots(辞書リスト)

    # spotsリストの要素: {'name': 場所名, 'lat': 緯度, 'long': 経度,
    # 'num_of_reviews': 口コミ数, 'review_rating': 評価}
    # ここでspots_json['spots']にspotの辞書リストの追加をお願いします
    spots_json['spots'] = google_func()  # <-google_func(place_name)
    return render(request, 'trip_maker/main.html', spots_json)
