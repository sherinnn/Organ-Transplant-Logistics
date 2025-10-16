import requests

def get_weather_forecast(origin: dict, dest: dict):
    url = "http://127.0.0.1:8000/mcp/get_weather_forecast"
    payload = {"origin": origin, "dest": dest}
    try:
        print("📡 Sending request to Gateway:", payload)
        resp = requests.post(url, json=payload, timeout=10)
        print("📬 Response code:", resp.status_code)
        print("📦 Raw response:", resp.text)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print("❌ Weather Gateway error:", e)
        return {"error": str(e)}
    

def track_flights(date: str, airport1: str, airport2: str):
    url = "http://127.0.0.1:8000/mcp/track_flights"
    payload = {
        "airport1": airport1,
        "airport2": airport2,
        "date": date
    }
    resp = requests.post(url, json=payload, timeout=10)
    resp.raise_for_status()
    return resp.json()
