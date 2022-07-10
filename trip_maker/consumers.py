import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

class tripConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'trip_maker_%s' % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        data_type = text_data_json['type']

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': data_type,
                'message': message
            }
        )

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))
    
    def spots_by_review_rating(self, event):
        spots_json = {'type': event['type'], 'spots': []}
        # TODO 与えられた緯度、経度から滞在人口が少ない and レビュー評価が高い
        # spotを上位20件を抽出。つまり、入力が緯度、経度で戻り値がspots(辞書リスト)
        
        # spotsリストの要素: {'name': 場所名, 'lat': 緯度, 'long': 経度, 
        # 'resident_population': 滞在人口, 'mobile_population': 移動人口, 
        # 'num_of_reviews': 口コミ数, 'review_rating': 評価}
        self.send(text_data=json.dumps(spots_json))