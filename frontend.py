import os
from http.server import SimpleHTTPRequestHandler, HTTPServer

DIRECTORY = "./frontend"
SERVER_ADDRESS = ("", 80)

httpd = HTTPServer(SERVER_ADDRESS, SimpleHTTPRequestHandler)
os.chdir(DIRECTORY)

print(
    f"Serving HTTP on port {SERVER_ADDRESS[1]} (http://localhost:{SERVER_ADDRESS[1]}/) ..."
)
httpd.serve_forever()
