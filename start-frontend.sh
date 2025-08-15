#!/usr/bin/env bash
# start-frontend.sh
# Navigates to apolotyreaibot and starts or restarts the frontend serve process on port 5000.
# Detached with nohup, output logged to serve.log, and disowned so it survives logout.

# 1) Change to the project directory
cd ~/apoloTyreSample || {
  echo "Directory ~/apolotyresample not found. Aborting."
  exit 1
}

# 2) Check if SSL certificates exist
if [ ! -f "./ssl/cert.pem" ] || [ ! -f "./ssl/key.pem" ]; then
    echo "SSL certificates not found. Generating self-signed certificates..."
    ./generate-ssl.sh
fi

# 3) Kill any existing process listening on port 3006
echo "Stopping any process on port 3006..."
lsof -ti:3006 | xargs -r kill -9

# 4) Start the static server on port 3006 with HTTPS, detach it, and log output
nohup npx serve apollo-widget -l 3006 --ssl-cert ./ssl/cert.pem --ssl-key ./ssl/key.pem > serve.log 2>&1 &
#nohup npx serve frontend -l 3006 --ssl-cert ./ssl/cert.pem --ssl-key ./ssl/key.pem > serve.log 2>&1 &

# 5) Prevent it from being killed when you close the SSH session
disown

echo "Frontend server restarted on port 3006 with HTTPS (logs → serve.log)"
