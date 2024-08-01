#!/bin/sh

ntfy serve --base-url http://localhost --upstream-base-url https://ntfy.sh --listen-http :8080 &
python ./tempi.py &
python ./ping.py
