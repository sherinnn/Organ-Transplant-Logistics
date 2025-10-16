# from flask import Flask, request, jsonify
# from gateway.weather_handler import handler as weather_handler
# from gateway.flight_handler import handler as flight_handler

# app = Flask(__name__)

# @app.route("/mcp/get_weather_forecast", methods=["POST"])
# def get_weather_forecast():
#     data = request.get_json()
#     result = weather_handler(data)
#     return jsonify(result), 200

# @app.route("/mcp/track_flights", methods=["POST"])
# def track_flights():
#     data = request.get_json()
#     result = flight_handler(data)
#     return jsonify(result), 200

# @app.route("/mcp/get_flight_info", methods=["POST"])
# def get_flight_info():
#     return jsonify(flight_handler({"body": request.get_json()}))

# if __name__ == "__main__":
#     app.run(port=8001)


import sys, os, traceback
from flask import Flask, request, jsonify

# --- Add path for local imports ---
sys.path.append(os.path.dirname(__file__))

# --- Import both handlers safely ---
try:
    from weather_handler import handler as weather_handler
    print("✅ Loaded weather_handler")
except Exception as e:
    print(f"💥 Could not import weather_handler: {e}")
    traceback.print_exc()

try:
    from flight_handler import handler as flight_handler
    print("✅ Loaded flight_handler")
except Exception as e:
    print(f"💥 Could not import flight_handler: {e}")
    traceback.print_exc()

# --- Initialize Flask ---
app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "🫀 OrganMatch MCP Gateway Active (Weather + Flight)"

# --- WEATHER ROUTE ---
@app.route("/mcp/get_weather_forecast", methods=["POST"])
def get_weather_forecast():
    try:
        print("🌤️ Received /mcp/get_weather_forecast")
        data = request.get_json(force=True)
        print(f"📦 Payload: {data}")
        result = weather_handler({"body": data})
        return jsonify(result)
    except Exception as e:
        print(f"💥 Weather route error: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# --- FLIGHT ROUTE ---
@app.route("/mcp/get_flight_info", methods=["POST"])
def get_flight_info():
    try:
        print("✈️ Received /mcp/get_flight_info")
        data = request.get_json(force=True)
        print(f"📦 Payload: {data}")
        result = flight_handler({"body": data})
        return jsonify(result)
    except Exception as e:
        print(f"💥 Flight route error: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("🌐 Starting Unified OrganMatch Gateway on port 8000...")
    app.run(host="127.0.0.1", port=8000, debug=True)
