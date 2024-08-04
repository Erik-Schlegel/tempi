#!/bin/sh

python ./tempi.py &
ntfy serve --base-url http://localhost --upstream-base-url https://ntfy.sh --listen-http :8080 &
gunicorn -k eventlet -w 1 -b 0.0.0.0:8000 api:app &
gunicorn -k eventlet -w 1 -b 0.0.0.0:80 frontend:app
