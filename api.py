from flask import Flask, jsonify, request
import logging

logging.basicConfig(
    filename="/tempi/log/api.log", level=logging.ERROR, format="%(message)s"
)

app = Flask(__name__)

tdata = {"initial": "value"}


@app.route("/", methods=["GET"])
def test():
    return jsonify({"response": "hello"})


@app.route("/data", methods=["UPDATE", "GET"])
def data():

    global tdata

    if request.method == "GET":
        try:
            return jsonify(tdata)
        except Exception as e:
            logging.error(e)
            return jsonify({"response": "error"})
    try:
        tdata = request.json
        return jsonify({"response": "success"})
    except Exception as e:
        logging.error(e)
        return jsonify({"response": "error"})


# if __name__ == "__main__":
#     app.run(debug=True, host="0.0.0.0", port=8000)
