#!/bin/sh

ntfy serve --base-url http://localhost --upstream-base-url https://ntfy.sh --listen-http :8080 &
python ./tempi.py &
gunicorn -k eventlet -w 1 -b 0.0.0.0:8000 api:app &
python ./preprocess_frontend.py && python ./frontend.py