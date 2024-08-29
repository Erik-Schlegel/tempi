import os
from flask import Flask, render_template, send_from_directory

api_url = os.getenv("API_URL")
latitude = os.getenv("LATITUDE")
longitude = os.getenv("LONGITUDE")
time_zone_id = os.getenv("TIME_ZONE_ID")
low_temp_desired_channel = os.getenv("LOW_TEMP_DESIRED_CHANNEL")
high_temp_expected_channel = os.getenv("HIGH_TEMP_EXPECTED_CHANNEL")
channels = os.getenv('CHANNELS')

if api_url is None:
    raise ValueError("API_URL environment variable must be set")

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True


@app.route("/")
def index():
    return render_template(
        "index.j2",
        API_URL=api_url,
        LATITUDE=latitude,
        LONGITUDE=longitude,
        TIME_ZONE_ID=time_zone_id,
        CHANNELS=channels,
        LOW_TEMP_DESIRED_CHANNEL=low_temp_desired_channel,
        HIGH_TEMP_EXPECTED_CHANNEL=high_temp_expected_channel
    )


@app.route('/static/client/<path:filename>')
def serve_client_files(filename):
    return send_from_directory('static/client', filename)
