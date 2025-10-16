from flask import Flask, request, jsonify
from gateway.weather_handler import handler as weather_handler
from gateway.flight_handler import handler as flight_handler

app = Flask(__name__)

@app.route("/mcp/get_weather_forecast", methods=["POST"])
def get_weather_forecast():
    data = request.get_json()
    result = weather_handler(data)
    return jsonify(result), 200

@app.route("/mcp/track_flights", methods=["POST"])
def track_flights():
    data = request.get_json()
    result = flight_handler(data)
    return jsonify(result), 200

if __name__ == "__main__":
    print("✅ MCP Gateway running at http://127.0.0.1:8000")
    app.run(host="0.0.0.0", port=8000)
