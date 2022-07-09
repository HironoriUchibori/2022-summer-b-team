import requests
import json
import pprint
import time
import datetime


def main():
    google_func2(36.1091117, 140.101429)
    # google_func("千葉県")


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
    # print(place['results'][0]["geometry"]["location"])
    # print(place['results'][0]["user_ratings_total"])
    # print(len(place['results']))
    # places = place['results']

    # for place in place["results"]:
    #   print(place["user_ratings_total"])
    #   print(place["name"])
    #   print(place["geometry"]["location"])

    # 受け取った都道府県から評価数が多い10個の場所を探す
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


def google_func2(lat, lon):
    url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?key=AIzaSyA5SmbNJlpGTV_v6aAtKS-caYI8OpNFQGg&location=' + str(
        lat) + ',' + str(lon) + '&radius=30000&language=ja&keyword=観光'
    payload = {}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    places = json.loads(response.text)
    #print(places)
    # pprint.pprint(places)
    rating = []
    location = []
    name = []
    for place in places["results"]:
        if place.get("rating") != None:
            location.append(place["geometry"]["location"])
            rating.append(place["rating"])
            name.append(place["name"])
    for i in range(2):
        time.sleep(1)
        if places.get("next_page_token") != None:
            url1 = url + '&pagetoken=' + places["next_page_token"]
            response = requests.request("GET",
                                        url1,
                                        headers=headers,
                                        data=payload)
            places = json.loads(response.text)
            for place in places["results"]:
                if place.get("rating") != None:
                    location.append(place["geometry"]["location"])
                    rating.append(place["rating"])
                    name.append(place["name"])
            # pprint.pprint(places)
            url1 = None
            #print(places["next_page_token"])
    # print(location)
    # print(rating)
    # print(name)
    population_func(location, rating, name)


# 有名なところの経度緯度取得
# その取得した緯度経度を基準としたある範囲を指定
def population_func(locations, rating, name):
    populations = []
    t_delta = datetime.timedelta(hours=9)
    JST = datetime.timezone(t_delta, 'JST')
    now = datetime.datetime.now(JST)
    past_delta = datetime.timedelta(weeks=1)
    past = now - past_delta
    # YYYYMMDDhhmmss形式に書式化
    now = now.strftime('%Y%m%d%H%M')
    past = past.strftime('%Y%m%d%H%M')
    # 受け取った緯度経度から人口を算出->スコア化
    average_population = []
    for location in locations:
        lat = location["lat"]
        lng = location["lng"]
        url = 'https://l955buebw3.execute-api.ap-northeast-1.amazonaws.com/vital-statistics/latlng'

        Headers = {
            "content-type": "application/json",
            "x-api-key": "mMKbSQgA3rRqwuzlE3aG5MNzUg0K1ak29FnaGJuf"
        }
        place = {
            "startLat": lat,
            "startLng": lng,
            "meshSize": 5,
            "timeUnit": 15,
            "startTime": str(past),  # あとで調整
            "endTime": str(now)
        }
        res = requests.post(url, headers=Headers, json=place)
        data = json.loads(res.text)
        # print(data)
        # pprint.pprint(
        #     data['body']['results'][0]['populationList'][0]["population"])
        for population_lists in data['body']['results']:
            population_array = []
            for population_list in population_lists["populationList"]:
                pop_num = population_list["population"]
                population_array.append(pop_num)
            pop_mean = sum(population_array) / len(population_array)
            # print(pop_mean)
            average_population.append(pop_mean)
    average = sum(average_population) / len(average_population)
    population_score = []
    for average_score in average_population:
        score = float(average / average_score)
        population_score.append(score)

    #population_scoreとrating_scoreを足し合わせる
    total_score = []
    rating_max = max(rating)
    population_max = max(population_score)
    for i in range(len(population_score)):
        rating_score = (rating[i]) / (rating_max)
        pop_score = (population_score[i]) / (population_max)
        score = pop_score + rating_score
        total_score.append(score)
    # print(f'total_score = {total_score}')

    # スコアの上位15個くらいの場所名を求める
    array = total_score
    top_n_location_lat = []
    top_n_location_lon = []
    top_n_name = []

    array = sorted(array, reverse=True)
    for i in range(15):  #上位何個取得するか
        num = array[i]
        total_score_index = total_score.index(num)
        top_n_location_lat.append(locations[total_score_index]['lat'])
        top_n_location_lon.append(locations[total_score_index]['lng'])
        top_n_name.append(name[total_score_index])
    print(top_n_name)

    # 人数の少ないところをピックアップ
    # Google place api からもらった評価の情報と合わせてフィルタリング

    # フィルタリングして合致したメッシュコードから緯度経度取得
    # 緯度経度情報から場所特定

    # # 250m = 0.0025°
    # one_km = 0.01
    # # lat:緯度
    # # lon:経度
    # start_lat = lat + 1 * one_km
    # end_lat = lat - 1 * one_km
    # start_lon = lon - 1 * one_km
    # end_lon = lon + 1 * one_km


if __name__ == "__main__":
    main()
