from django.shortcuts import render
from django.conf import settings
import json, os

# Create your views here.


def index(request):
    # TODO 47都道府県をリストを追加
    prefectures_json = {'prefectures': []}
    prefectures_json['prefectures'].append('hoge')
    prefectures_json['prefectures'].append('piyo')
    return render(request, 'trip_maker/index.html', prefectures_json)

def main(request, room_name):
    spots_json = {'room_name': room_name, 'spots': []}
    # TODO　都道府県名から滞在人口が少ない and 人気がある(口コミが多い)のスポットの
    # 上位10件を抽出。つまり、入力が都道府県名で戻り値がspots(辞書リスト)
    
    # spotsリストの要素: {'name': 場所名, 'lat': 緯度, 'long': 経度, 
    # 'resident_population': 滞在人口, 'mobile_population': 移動人口, 
    # 'num_of_reviews': 口コミ数, 'review_rating': 評価}
    # ここでspots_json['spots']にspotの辞書リストの追加をお願いします
    return render(request, 'trip_maker/main.html', spots_json)
