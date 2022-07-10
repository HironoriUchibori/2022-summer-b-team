import requests
import json
import pprint

url = 'https://l955buebw3.execute-api.ap-northeast-1.amazonaws.com/vital-statistics/latlng'

Headers = {
  "content-type":"application/json",
  "x-api-key":"mMKbSQgA3rRqwuzlE3aG5MNzUg0K1ak29FnaGJuf"
  }

place = {
  "startLat": 35.692429,
  "startLng": 139.699572,
  "endLat": 35.68985,
  "endLng": 139.704292,
  "meshSize": 5,
  "timeUnit": 15,
  "startTime": "202103010900",
  "endTime": "202103011000"
}

res = requests.post(url, headers=Headers,json=place)

data = json.loads(res.text)
pprint.pprint(data)
