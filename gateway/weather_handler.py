import os
import requests
import json
import datetime
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get("WEATHERAPI_KEY")
BASE_URL = "http://api.weatherapi.com/v1/current.json"

def fetch_weather_query(query):
    params = {
        "key": API_KEY,
        "q": query,
        "aqi": "no"
    }
    resp = requests.get(BASE_URL, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()

def simplify_weather(resp: dict):
    """
    Pick relevant parts from WeatherAPI response
    Example structure: { "location": {...}, "current": {...} } :contentReference[oaicite:2]{index=2}
    """
    loc = resp.get("location", {})
    cur = resp.get("current", {})
    return {
        "location": {
            "name": loc.get("name"),
            "region": loc.get("region"),
            "country": loc.get("country"),
            "lat": loc.get("lat"),
            "lon": loc.get("lon"),
            "tz_id": loc.get("tz_id"),
            "localtime": loc.get("localtime")
        },
        "current": {
            "last_updated": cur.get("last_updated"),
            "temp_c": cur.get("temp_c"),
            "temp_f": cur.get("temp_f"),
            "condition": cur.get("condition"),  # condition.text, icon, code
            "wind_mph": cur.get("wind_mph"),
            "wind_kph": cur.get("wind_kph"),
            "wind_degree": cur.get("wind_degree"),
            "wind_dir": cur.get("wind_dir"),
            "pressure_mb": cur.get("pressure_mb"),
            "precip_mm": cur.get("precip_mm"),
            "humidity": cur.get("humidity"),
            "cloud": cur.get("cloud"),
            "feelslike_c": cur.get("feelslike_c"),
            "vis_km": cur.get("vis_km"),
            "gust_kph": cur.get("gust_kph"),
        }
    }

def handler(event, context=None):
    payload = event.get("body")
    if isinstance(payload, str):
        payload = json.loads(payload)
    elif payload is None:
        payload = event

    origin = payload["origin"]
    dest = payload["dest"]

    def resolve_query(location):
        # Accept either city/state or lat/lon
        if "lat" in location and "lon" in location:
            return f"{location['lat']},{location['lon']}"
        elif "city" in location:
            # Build query string like "Los Angeles,CA"
            state = location.get("state", "")
            return f"{location['city']},{state}".strip(",")
        else:
            raise ValueError("Invalid location format. Must include 'lat/lon' or 'city/state'.")

    try:
        o_query = resolve_query(origin)
        d_query = resolve_query(dest)

        o_resp = fetch_weather_query(o_query)
        d_resp = fetch_weather_query(d_query)

        origin_weather = simplify_weather(o_resp)
        dest_weather = simplify_weather(d_resp)

        risk_flags = []
        if origin_weather["current"]["wind_kph"] > 40:
            risk_flags.append("HighWindOrigin")
        if dest_weather["current"]["wind_kph"] > 40:
            risk_flags.append("HighWindDest")

        recommendation = "Proceed" if not risk_flags else "Delay or reroute"

        expires = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
        expires_at = expires.isoformat() + "Z"

        return {
            "origin_weather": origin_weather,
            "dest_weather": dest_weather,
            "risk_flags": risk_flags,
            "recommendation": recommendation,
            "expires_at": expires_at
        }
    except Exception as e:
        print("❌ Gateway error:", e)
        return {"error": str(e)}, 500
