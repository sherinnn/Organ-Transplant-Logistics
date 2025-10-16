# from strands import tool
# import requests
# from datetime import datetime
# from strands.models import BedrockModel


# def calculate_duration(departure: str, arrival: str):
#     """Estimate duration in minutes from readable timestamps (e.g. '06:00, Oct 20')."""
#     try:
#         d = datetime.strptime(departure, "%H:%M, %b %d")
#         a = datetime.strptime(arrival, "%H:%M, %b %d")
#         if a < d:
#             a = a.replace(day=a.day + 1)
#         return int((a - d).total_seconds() / 60)
#     except Exception:
#         return None


# @tool
# def track_flights_tool(api_key: str, date: str, airport1: str, airport2: str, use_bedrock: bool = True):
#     """
#     Fetch flights between two airports using FlightAPI, sorted by least duration.
#     """
#     url = f"https://api.flightapi.io/trackbyroute/{api_key}?date={date}&airport1={airport1}&airport2={airport2}"
#     resp = requests.get(url)
#     if resp.status_code != 200:
#         return {"error": f"FlightAPI error {resp.status_code}: {resp.text}"}

#     data = resp.json()
#     flights = data.get("flights", [])
#     if not flights:
#         return {"error": "No flight data found."}

#     enriched = []
#     for f in flights:
#         dep, arr = f.get("departureTime"), f.get("arrivalTime")
#         duration = calculate_duration(dep, arr)
#         # Format date as YYYY-MM-DD (Google expects this format)
#         date_fmt = f"{date[:4]}-{date[4:6]}-{date[6:]}"

#         # Build a working Google Flights search link
#         booking_url = (
#             f"https://www.google.com/flights?hl=en#flt={airport1}.{airport2}.{date_fmt}*{airport2}.{airport1}.{date_fmt}"
#         )


#         enriched.append({
#             "Airline": f.get("airline"),
#             "FlightNumber": f.get("flightNumber"),
#             "DepartureTime": dep,
#             "ArrivalTime": arr,
#             "DurationMinutes": duration,
#             "BookingLink": booking_url
#         })

#     valid = [f for f in enriched if f["DurationMinutes"] is not None]
#     flights_sorted = sorted(valid, key=lambda x: x["DurationMinutes"])

#     output = {"top_flights": flights_sorted[:5]}

#     # Optional: Bedrock summary
#     if use_bedrock and flights_sorted:
#         try:
#             model = BedrockModel(model_id="anthropic.claude-3-haiku-20240307")
#             prompt = (
#                 f"You are an organ transport logistics AI.\n"
#                 f"Summarize the best {len(flights_sorted[:5])} flights between {airport1} and {airport2}:\n"
#                 f"{flights_sorted[:5]}\n"
#                 "Summarize the fastest flight and mention airline, flight number, duration, and booking link."
#             )
#             res = model.invoke(input=prompt)
#             output["summary"] = res.get("output_text", "") if isinstance(res, dict) else res
#         except Exception as e:
#             output["summary_error"] = str(e)

#     return output




from strands import tool
import requests
from datetime import datetime
from urllib.parse import quote_plus
from strands.models import BedrockModel


def calculate_duration(departure: str, arrival: str):
    """Estimate duration in minutes from readable timestamps (e.g. '06:00, Oct 20')."""
    try:
        d = datetime.strptime(departure, "%H:%M, %b %d")
        a = datetime.strptime(arrival, "%H:%M, %b %d")
        if a < d:
            a = a.replace(day=a.day + 1)
        return int((a - d).total_seconds() / 60)
    except Exception:
        return None


from urllib.parse import quote_plus

def build_google_flights_link(origin: str, dest: str, yyyymmdd: str, airline: str | None = None, flight_number: str | None = None):
    """Generate a one-way Google Flights link that searches for a specific flight if possible."""
    yyyy, mm, dd = yyyymmdd[:4], yyyymmdd[4:6], yyyymmdd[6:]
    date_str = f"{yyyy}-{mm}-{dd}"

    # Build natural-language search query
    if airline and flight_number:
        query = f"{airline} flight {flight_number} from {origin} to {dest} on {date_str}"
    elif airline:
        query = f"{airline} flights from {origin} to {dest} on {date_str}"
    else:
        query = f"Flights from {origin} to {dest} on {date_str}"

    encoded = quote_plus(query)
    return f"https://www.google.com/travel/flights?q={encoded}"


def build_alternative_links(origin: str, dest: str, yyyymmdd: str):
    """Generate backup aggregator links for reliability."""
    yyyy, mm, dd = yyyymmdd[:4], yyyymmdd[4:6], yyyymmdd[6:]
    date_str = f"{yyyy}-{mm}-{dd}"
    yymmdd = f"{yyyy[2:]}{mm}{dd}"

    kayak = f"https://www.kayak.com/flights/{origin}-{dest}/{date_str}?sort=duration_a"
    skyscanner = f"https://www.skyscanner.com/transport/flights/{origin.lower()}/{dest.lower()}/{yymmdd}/?adults=1&trip=oneway"
    expedia = (
        "https://www.expedia.com/Flights-Search"
        f"?trip=oneway&leg1=from:{origin},to:{dest},departure:{mm}/{dd}/{yyyy}TANYT"
        "&passengers=adults:1&options=cabinclass:economy&mode=search"
    )

    return {
        "google_flights": build_google_flights_link(origin, dest, yyyymmdd),
        "kayak": kayak,
        "skyscanner": skyscanner,
        "expedia": expedia,
    }


@tool
def track_flights_tool(api_key: str, date: str, airport1: str, airport2: str, use_bedrock: bool = True):
    """
    Fetch flights between two airports using FlightAPI, sorted by shortest duration.
    Returns top flights with multiple working booking links.
    """
    url = f"https://api.flightapi.io/trackbyroute/{api_key}?date={date}&airport1={airport1}&airport2={airport2}"
    resp = requests.get(url)
    if resp.status_code != 200:
        return {"error": f"FlightAPI error {resp.status_code}: {resp.text}"}

    data = resp.json()
    flights = data.get("flights", [])
    if not flights:
        return {"error": "No flight data found."}

    enriched = []
    for f in flights:
        dep, arr = f.get("departureTime"), f.get("arrivalTime")
        duration = calculate_duration(dep, arr)
        links = build_alternative_links(airport1, airport2, date)
        links["google_flights"] = build_google_flights_link(
            origin=airport1,
            dest=airport2,
            yyyymmdd=date,
            airline=f.get("airline"),
            flight_number=f.get("flightNumber"),
)


        enriched.append({
            "Airline": f.get("airline"),
            "FlightNumber": f.get("flightNumber"),
            "DepartureTime": dep,
            "ArrivalTime": arr,
            "DurationMinutes": duration,
            "BookingLinks": links,
        })

    valid = [f for f in enriched if f["DurationMinutes"] is not None]
    flights_sorted = sorted(valid, key=lambda x: x["DurationMinutes"])

    output = {"top_flights": flights_sorted[:5]}

    if use_bedrock and flights_sorted:
        try:
            model = BedrockModel(model_id="anthropic.claude-3-haiku-20240307")
            prompt = (
                f"You are an organ transport logistics AI.\n"
                f"Summarize the best {len(flights_sorted[:5])} flights between {airport1} and {airport2}:\n"
                f"{flights_sorted[:5]}\n"
                "Summarize the fastest flight and include airline, number, duration, and booking link."
            )
            res = model.invoke(input=prompt)
            output["summary"] = res.get("output_text", "") if isinstance(res, dict) else res
        except Exception as e:
            output["summary_error"] = str(e)

    return output
