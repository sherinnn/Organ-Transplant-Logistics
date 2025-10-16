import requests, os

API_KEY = "e3cd038ddfa240adbd7163041251610"
print("API key:", API_KEY)

resp = requests.get("http://api.weatherapi.com/v1/current.json", params={
    "key": API_KEY,
    "q": "Los Angeles"
})
print(resp.status_code)
print(resp.json())
