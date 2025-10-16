import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def calculate_duration(departure: str, arrival: str):
    try:
        d = datetime.strptime(departure, "%H:%M, %b %d")
        a = datetime.strptime(arrival, "%H:%M, %b %d")
        if a < d:
            a = a.replace(day=a.day + 1)
        return int((a - d).total_seconds() / 60)
    except Exception as e:
        print(f"⚠️ Duration calc error: {e}")
        return None


def handler(event, context=None):
    """Gateway MCP handler for FlightAPI route lookups."""
    try:
        payload = event.get("body")
        if isinstance(payload, str):
            payload = json.loads(payload)
        elif payload is None:
            payload = event

        api_key = os.getenv("FLIGHT_API")
        date = payload.get("date")
        airport1 = payload.get("origin")
        airport2 = payload.get("dest")

        print(f"📩 Received payload: {payload}")
        print(f"🔑 API Key: {'SET' if api_key else 'NOT SET'}")

        if not api_key:
            raise ValueError("Missing FLIGHT_API_KEY in environment")

        if not (date and airport1 and airport2):
            raise ValueError("Missing required parameters: 'date', 'origin', 'dest'")

        # Build FlightAPI URL
        url = f"https://api.flightapi.io/trackbyroute/{api_key}?date={date}&airport1={airport1}&airport2={airport2}"
        print(f"🌍 Requesting: {url}")

        resp = requests.get(url, timeout=15)
        print(f"📡 Response Code: {resp.status_code}")

        if resp.status_code != 200:
            print(f"❌ API Error: {resp.text}")
            return {"error": f"FlightAPI error {resp.status_code}: {resp.text}"}

        data = resp.json()
        print(f"✅ Parsed JSON keys: {list(data.keys())}")

        flights = data.get("flights", [])
        if not flights:
            print("⚠️ No flights found.")
            return {"error": "No flight data found for this route/date."}

        enriched = []
        for f in flights:
            dep = f.get("departureTime")
            arr = f.get("arrivalTime")
            duration = calculate_duration(dep, arr)
            enriched.append({
                "Airline": f.get("airline"),
                "FlightNumber": f.get("flightNumber"),
                "DepartureTime": dep,
                "ArrivalTime": arr,
                "DurationMinutes": duration,
            })

        valid = [f for f in enriched if f["DurationMinutes"] is not None]
        flights_sorted = sorted(valid, key=lambda x: x["DurationMinutes"])

        return {"top_flights": flights_sorted[:5]}

    except Exception as e:
        print(f"💥 Handler crashed: {e}")
        return {"error": str(e)}
