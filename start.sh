#!/bin/sh
ntfy serve --base-url http://localhost --upstream-base-url https://ntfy.sh &
python ./tempi.py