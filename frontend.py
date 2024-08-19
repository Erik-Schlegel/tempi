import os
from flask import Flask, render_template, send_from_directory

api_url = os.getenv("API_URL")
latitude = os.getenv("LATITUDE")
longitude = os.getenv("LONGITUDE")
time_zone_id = os.getenv("TIME_ZONE_ID")

if api_url is None:
    raise ValueError("API_URL environment variable must be set")

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True


@app.route("/")
def index():
    return render_template("index.html", API_URL=api_url, LATITUDE=latitude, LONGITUDE=longitude, TIME_ZONE_ID=time_zone_id)


@app.route('/static/client/<path:filename>')
def serve_client_files(filename):
    return send_from_directory('static/client', filename)
