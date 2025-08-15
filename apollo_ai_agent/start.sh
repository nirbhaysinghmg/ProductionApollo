#!/bin/bash

# Define variables
APP_MODULE="main:app"
PORT=${1:-9006} # get port from first argument, default to 9006
LOG_FILE="realtyseek.log"

# Stop any running instance on the same port before starting
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$SCRIPT_DIR/stop.sh" "$PORT"

echo "Starting Uvicorn server with SSL on port $PORT..."

# Check if SSL certificates exist
if [ -f "../ssl/cert.pem" ] && [ -f "../ssl/key.pem" ]; then
    echo "SSL certificates found. Starting with HTTPS..."
    nohup uvicorn $APP_MODULE --host 0.0.0.0 --port $PORT --ssl-keyfile ../ssl/key.pem --ssl-certfile ../ssl/cert.pem > $LOG_FILE 2>&1 &
else
    echo "SSL certificates not found. Starting without HTTPS..."
    nohup uvicorn $APP_MODULE --host 0.0.0.0 --port $PORT > $LOG_FILE 2>&1 &
fi

echo "Uvicorn server started in the background. Output is in $LOG_FILE"
echo "Server should now be running on https://localhost:$PORT"
