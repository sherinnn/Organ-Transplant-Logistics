from flight_tool import track_flights_tool
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("FLIGHT_API")

result = track_flights_tool(api_key=api_key, date="20251020", airport1="LAX", airport2="JFK", use_bedrock=False)

print("Top Flights:\n")
for f in result.get("top_flights", []):
    print(f"- {f['Airline']} {f['FlightNumber']} | {f['DepartureTime']} → {f['ArrivalTime']} | {f['DurationMinutes']} min")
    print("  Google Flights:", f["BookingLinks"]["google_flights"])
    print("  Kayak:", f["BookingLinks"]["kayak"])
    print("  Skyscanner:", f["BookingLinks"]["skyscanner"])
    print("  Expedia:", f["BookingLinks"]["expedia"])
    print()
