#!/bin/bash

# Get port from the first argument, default to 9002 if not provided.
PORT=${1:-9006}

echo "Looking for process listening on port $PORT..."

# Find process IDs listening on the specified TCP port.
PIDS=$(lsof -ti tcp:$PORT)

if [ -z "$PIDS" ]; then
  echo "No process found listening on port $PORT."
  exit 0
fi

echo "Found process(es) with PID(s): $PIDS"
for PID in $PIDS; do
  echo "Stopping process with PID $PID..."
  kill $PID
done

echo "Process(es) on port $PORT stopped."

