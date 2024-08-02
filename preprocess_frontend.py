from jinja2 import Environment, FileSystemLoader
import os
import logging

logging.basicConfig(
    filename="/tempi/log/preprocess.log", level=logging.DEBUG, format="%(message)s"
)

env = Environment(loader=FileSystemLoader("frontend"))
template = env.get_template("index.pre.html")

api_url = os.getenv("API_URL", "https://localhost:8000")
logging.debug(f"API_URL: {api_url}")
rendered_html = template.render(API_URL=api_url)

with open("frontend/index.html", "w") as f:
    f.write(rendered_html)
