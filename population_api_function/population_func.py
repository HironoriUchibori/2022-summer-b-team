import requests
import json
import pprint

def main():
  decision_scope(35.692429, 139.699572)
  # google_func("千葉県")

def google_func(place_name):
  params = {
      "query": place_name + " 観光",
      "key":"AIzaSyA5SmbNJlpGTV_v6aAtKS-caYI8OpNFQGg",
      "region" : "jp",
      "language" : "ja",
      }

  google_api_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"

  res = requests.get(google_api_url, params= params)
  place = json.loads(res.text)
  # print(place['results'][0]["geometry"]["location"])
  # print(place['results'][0]["user_ratings_total"])
  # print(len(place['results']))
  # places = place['results']

  # for place in place["results"]:
  #   print(place["user_ratings_total"])
  #   print(place["name"])
  #   print(place["geometry"]["location"])

  #受け取った都道府県から評価数が多い10個の場所を探す
  rating_total = []
  array = []
  location = []
  top_ten_location = []
  name = []
  top_ten_name = []

  for place in place["results"]:
    location.append(place["geometry"]["location"])
    rating_total.append(place["user_ratings_total"])
    name.append(place["name"])
    array.append(place["user_ratings_total"])

  array = sorted(array, reverse=True)
  for i in range(10):
    num = array[i]
    rating_index = rating_total.index(num)
    top_ten_location.append(location[rating_index])
    top_ten_name.append(name[rating_index])





#有名なところの経度緯度取得
#その取得した緯度経度を基準としたある範囲を指定
def decision_scope(lat, lon):
  #250m = 0.0025°
  one_km = 0.01
  #lat:緯度
  #lon:経度
  start_lat = lat + 1 * one_km
  end_lat = lat - 1 * one_km
  start_lon = lon - 1 * one_km
  end_lon = lon + 1 * one_km

  #その範囲内での滞在人数を取得

  url = 'https://l955buebw3.execute-api.ap-northeast-1.amazonaws.com/vital-statistics/latlng'

  Headers = {
    "content-type":"application/json",
    "x-api-key":"mMKbSQgA3rRqwuzlE3aG5MNzUg0K1ak29FnaGJuf"
    }

  place = {
    "startLat": start_lat,
    "startLng": start_lon,
    "endLat": end_lat,
    "endLng": end_lon,
    "meshSize": 5,
    "timeUnit": 15,
    "startTime": "202103010900", #あとで調整
    "endTime": "202103011000"
  }

  res = requests.post(url, headers=Headers,json=place)

  data = json.loads(res.text)
  pprint.pprint(data)
  # print(data['meshCode'])
  # for k in data:
  #   print(k)
  print(data['body']['results'][0])

  #人数の少ないところをピックアップ
  #Google place api からもらった評価の情報と合わせてフィルタリング

  #フィルタリングして合致したメッシュコードから緯度経度取得
  #緯度経度情報から場所特定

if __name__ == "__main__":
    main()
