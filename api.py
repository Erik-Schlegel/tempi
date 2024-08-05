import os
from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import logging

logging.basicConfig(
    filename="/tempi/log/api.log", level=logging.ERROR, format="%(message)s"
)

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


# run me with gunicorn
