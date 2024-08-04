import os
from flask import Flask, render_template_string
from jinja2 import Environment, FileSystemLoader


app = Flask(__name__)

env = Environment(loader=FileSystemLoader("frontend"))
template = env.get_template("index.pre.html")


@app.route("/")
def index():
    api_url = os.getenv("API_URL", "http://localhost:8000")
    rendered_html = template.render(API_URL=api_url)
    return render_template_string(rendered_html)
