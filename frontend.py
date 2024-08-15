import os
from flask import Flask, render_template_string, send_from_directory
from jinja2 import Environment, FileSystemLoader

api_url = os.getenv("API_URL")
latitude = os.getenv("LATITUDE")
longitude = os.getenv("LONGITUDE")
time_zone_id = os.getenv("TIME_ZONE_ID")


if api_url is None:
    raise ValueError("API_URL environment variable must be set")

app = Flask(__name__)

env = Environment(loader=FileSystemLoader("frontend"))
template = env.get_template("index.html")


@app.route("/")
def index():
    rendered_html = template.render(API_URL=api_url, LATITUDE=latitude, LONGITUDE=longitude, TIME_ZONE_ID=time_zone_id)
    return render_template_string(rendered_html)


@app.route('/client/<path:filename>')
def serve_client_files(filename):
    return send_from_directory('frontend/client', filename)
