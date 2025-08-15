#!/usr/bin/env bash
# restart-backend.sh

# 1) Check if SSL certificates exist
if [ ! -f "./ssl/cert.pem" ] || [ ! -f "./ssl/key.pem" ]; then
    echo "SSL certificates not found. Generating self-signed certificates..."
    ./generate-ssl.sh
fi

# 2) Kill any existing Python processes running the app
pkill -f "python.*app/main.py"
pkill -f "python.*-m app.main"

# 3) Give it a second to shut down (optional)
sleep 1

# 4) Start the new one using the modular structure with HTTPS
nohup python3 -m app.main > backend.log 2>&1 &
disown

echo "Backend restarted with HTTPS (logs → backend.log)"
