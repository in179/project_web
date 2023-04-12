import requests

url = "http://127.0.0.1:5000"
rr = url + "/get_data"
request = requests.get(rr)
print(request)
print(request.json())