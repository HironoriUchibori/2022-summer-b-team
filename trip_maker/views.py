from django.shortcuts import render
import requests
import json, os
import pprint
import time
import datetime

# Create your views here.


def index(request):
    # TODO 47都道府県をリストを追加
    PROVNAME = [
        '北海道', '青森県', '岩手県', '宮城県', '秋田県', '山形県', '福島県', '茨城県', '栃木県', '群馬県',
        '埼玉県', '千葉県', '東京都', '神奈川県', '新潟県', '富山県', '石川県', '福井県', '山梨県', '長野県',
        '岐阜県', '静岡県', '愛知県', '三重県', '滋賀県', '京都府', '大阪府', '兵庫県', '奈良県', '和歌山県',
        '鳥取県', '島根県', '岡山県', '広島県', '山口県', '徳島県', '香川県', '愛媛県', '高知県', '福岡県',
        '佐賀県', '長崎県', '熊本県', '大分県', '宮崎県', '鹿児島県', '沖縄県'
    ]
    prefectures_json = {'prefectures': []}
    prefectures_json['prefectures'] = PROVNAME
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
    place_name = request.GET.get('prefecture')
    # spotsリストの要素: {'name': 場所名, 'lat': 緯度, 'long': 経度,
    # 'num_of_reviews': 口コミ数, 'review_rating': 評価}
    # ここでspots_json['spots']にspotの辞書リストの追加をお願いします
    spots_json['spots'] = google_func(place_name)  # <-google_func(place_name)
    return render(request, 'trip_maker/main.html', spots_json)
