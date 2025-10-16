from agents.organ_logistics_agent import organ_logistics_agent
from dotenv import load_dotenv
import os

load_dotenv()
flight_api = os.getenv("FLIGHT_API")

response = organ_logistics_agent.run({
    "api_key": flight_api,
    "date": "20251020",
    "airport1": "LAX",
    "airport2": "JFK"
})

print(response)
