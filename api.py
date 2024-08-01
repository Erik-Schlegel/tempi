from flask import Flask, jsonify, request
import logging

logging.basicConfig(
    filename="/tempi/log/api.log", level=logging.ERROR, format="%(message)s"
)

app = Flask(__name__)

weather_data = {"initial": "value"}


@app.route("/", methods=["GET"])
def test():
    return jsonify({"response": "hello"})


@app.route("/data", methods=["UPDATE", "GET"])
def data():

    global weather_data

    if request.method == "GET":
        try:
            return jsonify(weather_data)
        except Exception as e:
            logging.error(e)
            return jsonify({"response": "error"})
    try:
        weather_data = request.json
        return jsonify({"response": "success"})
    except Exception as e:
        logging.error(e)
        return jsonify({"response": "error"})


# run me with gunicorn
