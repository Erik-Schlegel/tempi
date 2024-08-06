import os
from flask import Flask, render_template_string
from jinja2 import Environment, FileSystemLoader

api_url = os.getenv("API_URL")
if api_url is None:
    raise ValueError("API_URL environment variable must be set")

app = Flask(__name__)

env = Environment(loader=FileSystemLoader("frontend"))
template = env.get_template("index.html")


@app.route("/")
def index():
    rendered_html = template.render(API_URL=api_url)
    return render_template_string(rendered_html)
