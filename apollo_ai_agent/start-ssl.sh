#!/bin/bash

# start-ssl.sh - Start Apollo AI Agent backend with SSL/HTTPS

# Define variables
APP_MODULE="main:app"
PORT=${1:-9006}
LOG_FILE="realtyseek.log"

echo "🚀 Starting Apollo AI Agent backend with SSL on port $PORT..."

# Check if SSL certificates exist
if [ ! -f "../ssl/cert.pem" ] || [ ! -f "../ssl/key.pem" ]; then
    echo "❌ SSL certificates not found in ../ssl/ directory!"
    echo "Please run ./generate-ssl.sh from the root directory first."
    exit 1
fi

echo "✅ SSL certificates found. Starting with HTTPS..."

# Kill any existing processes on the port
echo "🔄 Stopping any existing processes on port $PORT..."
pkill -f "uvicorn.*$PORT" || true
sleep 2

# Start the server with SSL
nohup uvicorn $APP_MODULE \
    --host 0.0.0.0 \
    --port $PORT \
    --ssl-keyfile ../ssl/key.pem \
    --ssl-certfile ../ssl/cert.pem \
    > $LOG_FILE 2>&1 &

# Get the process ID
PID=$!
echo "✅ Backend started with PID: $PID"
echo "🌐 Server is now running on: https://localhost:$PORT"
echo "📝 Logs are being written to: $LOG_FILE"
echo "🔒 SSL is enabled - WebSocket connections should work!"
echo ""
echo "To stop the server, run: ./stop.sh"
echo "To view logs: tail -f $LOG_FILE"


