import requests
import json
import pprint

request = f'http://127.0.0.1:8000/post'
with open('request.json', 'r') as f:
    data = json.load(f)

response = requests.post(request, json=data)
#res = response.json()
pprint.pprint(response.json())