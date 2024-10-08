import os
from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from measurement_table import MeasurementTable
from logger import create_logger

logger = create_logger("api_logger", "api.log")

logger.debug("Starting API")


ALLOWED_ORIGINS = [os.environ.get("WWW_URL")]
app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": ALLOWED_ORIGINS}})
socketio = SocketIO(app, cors_allowed_origins=ALLOWED_ORIGINS)

weather_data = {}


@app.route("/test", methods=["GET"])
def test():
    return jsonify({"response": "success"}), 200


@app.route("/data", methods=["GET"])
def get_weather_data():
    return jsonify(weather_data), 200


@app.route("/data", methods=["UPDATE"])
def post_weather_data():
    global weather_data
    weather_data = request.json
    socketio.emit("weather_update", weather_data)
    return jsonify({"response": "success"}), 200




@socketio.on("connect")
def handle_connect():
    print("Client connected")
    emit("weather_update", weather_data)


@socketio.on("request_quantized_time")
def handle_request_quantized_time(data):
    try:
        logger.debug(f"Received request for quantized time with {data}")
        measurement_table = MeasurementTable()
        quantized_time = measurement_table.round_time()
        emit("quantized_time", str(quantized_time))
    except Exception as e:
        logger.error(f"Error in handle_request_quantized_time: {e}")


@socketio.on("request_historical_temps")
def handle_request_historical_data(data):
    logger.debug(f"Received request for historical temps with data: {data}")
    channels = data.get("channels", [])
    measurement_table = MeasurementTable()
    historical_temps = []

    for channel in channels:
        temps = measurement_table.get_historical_temps(channel, 24 * 60, 15)
        historical_temps.append({"channel": channel, "temps": temps})

    emit("historical_temps", historical_temps)


# run me with gunicorn
