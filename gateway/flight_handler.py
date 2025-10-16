import os
import json
import requests
from datetime import datetime

CACHE_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "flights_cache.json")

def calculate_duration(departure: str, arrival: str):
    """Estimate duration in minutes from readable timestamps (e.g., '06:00, Oct 20')."""
    try:
        d = datetime.strptime(departure, "%H:%M, %b %d")
        a = datetime.strptime(arrival, "%H:%M, %b %d")
        if a < d:
            a = a.replace(day=a.day + 1)
        return int((a - d).total_seconds() / 60)
    except Exception:
        return None


def load_cached_flights(origin: str, dest: str):
    """Retrieve flights from local cache JSON."""
    route_key = f"{origin.upper()}-{dest.upper()}"
    try:
        with open(CACHE_FILE, "r") as f:
            data = json.load(f)
        return data.get(route_key, [])
    except Exception as e:
        return {"error": f"Cache load failed: {e}"}


def handler(event, context=None):
    """MCP Gateway-compatible flight retrieval with cache fallback."""
    payload = event.get("body")
    if isinstance(payload, str):
        payload = json.loads(payload)
    elif payload is None:
        payload = event

    origin = payload.get("origin")
    dest = payload.get("dest")
    date = payload.get("date", "2025-10-20")

    # --- Step 1: Try cached data first ---
    cached = load_cached_flights(origin, dest)
    if isinstance(cached, list) and cached:
        return {"top_flights": cached, "source": "cache"}

    # --- Step 2: Optional live API fallback (disabled if no key present) ---
    api_key = os.getenv("FLIGHT_API_KEY")
    if not api_key:
        return {"error": "No flight data found in cache and no API key set."}

    url = f"https://api.flightapi.io/trackbyroute/{api_key}?date={date}&airport1={origin}&airport2={dest}"
    try:
        resp = requests.get(url)
        if resp.status_code != 200:
            return {"error": f"FlightAPI error {resp.status_code}: {resp.text}"}
        data = resp.json().get("flights", [])
        if not data:
            return {"error": "No flight data found."}

        enriched = []
        for f in data[:5]:
            dep, arr = f.get("departureTime"), f.get("arrivalTime")
            enriched.append({
                "Airline": f.get("airline"),
                "FlightNumber": f.get("flightNumber"),
                "DepartureTime": dep,
                "ArrivalTime": arr,
                "DurationMinutes": calculate_duration(dep, arr)
            })
        return {"top_flights": enriched, "source": "api"}
    except Exception as e:
        return {"error": f"Live API call failed: {e}"}
