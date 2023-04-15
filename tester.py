import requests

url = "https://dsfsdfdsf.pythonanywhere.com"
rr = url + "/test"
data = {"l": "text"}
request = requests.post(rr, json=data)
print(request)
print(request.json())