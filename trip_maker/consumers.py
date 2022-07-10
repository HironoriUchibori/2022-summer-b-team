import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import requests
import json
import pprint
import time
import datetime


class tripConsumer(WebsocketConsumer):

    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'trip_maker_%s' % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(self.room_group_name,
                                                    self.channel_name)

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(self.room_group_name,
                                                        self.channel_name)

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        data_type = text_data_json['type']

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(self.room_group_name, {
            'type': data_type,
            'message': message
        })

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps({'message': message}))

    def google_func2(self, lat, lon):
        url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?key=AIzaSyA5SmbNJlpGTV_v6aAtKS-caYI8OpNFQGg&location=' + str(
            lat) + ',' + str(lon) + '&radius=30000&language=ja&keyword=観光'
        payload = {}
        headers = {}
        response = requests.request("GET", url, headers=headers, data=payload)
        places = json.loads(response.text)
        rating = []
        location = []
        name = []
        for place in places["results"]:
            if place.get("rating") != None:
                location.append(place["geometry"]["location"])
                rating.append(place["rating"])
                name.append(place["name"])
        for i in range(2):
            # time.sleep(2)
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
                url1 = None
        population_func(location, rating, name)

    # 有名なところの経度緯度取得
    # その取得した緯度経度を基準としたある範囲を指定
    def population_func(self, locations, rating, name):
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
                "startTime": str(past),
                "endTime": str(now)
            }
            res = requests.post(url, headers=Headers, json=place)
            data = json.loads(res.text)
            for population_lists in data['body']['results']:
                population_array = []
                for population_list in population_lists["populationList"]:
                    pop_num = population_list["population"]
                    population_array.append(pop_num)
                pop_mean = sum(population_array) / len(population_array)
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

        # スコアの上位15個くらいの場所名を求める
        array = total_score
        return_val = []
        array = sorted(array, reverse=True)
        for i in range(15):  #上位何個取得するか
            num = array[i]
            total_score_index = total_score.index(num)
            place_info = dict.fromkeys(
                ['name', 'lat', 'long', 'population', 'review_rating'])
            place_info['name'] = name[total_score_index]
            place_info['lat'] = locations[total_score_index]['lat']
            place_info['long'] = locations[total_score_index]['lng']
            place_info['population'] = average_population[total_score_index]
            place_info['review_rating'] = rating[total_score_index]
            return_val.append(place_info)
        return return_val

    def spots_by_review_rating(self, event):
        spots_json = {'type': event['type'], 'spots': []}
        # TODO 与えられた緯度、経度から滞在人口が少ない and レビュー評価が高い
        # spotを上位15件を抽出。つまり、入力が緯度、経度で戻り値がspots(辞書リスト)
        location = event['message']
        lat = location['lat']
        lng = location['long']
        spots_json['spots'] = google_func2(lat, lng)
        # spotsリストの要素: {'name': 場所名, 'lat': 緯度, 'long': 経度,
        # 'population': 平均人口,
        # 'review_rating': 評価}
        self.send(text_data=json.dumps(spots_json))
