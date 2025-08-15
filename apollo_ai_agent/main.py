# main.py
import json
import time
import logging
from datetime import datetime
from fastapi import FastAPI, Request, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from chat_handler import chat_endpoint
from chat_history import chat_history_router
from feedback import feedback_router
from admin_router import admin_router
from guest_router import router as guest_router
from auth_router import router as auth_router
from main_agent_api import router as agent_router
from logger import logger, error_logger, log_query
from analytics import router as analytics_router

# -------------------
# Logging Setup
# -------------------
logging.basicConfig(level=logging.INFO)

# Example: Log server startup
logger.info("Apollo Tyres AI backend starting up...")

# -------------------
# FastAPI App Setup
# -------------------
app = FastAPI()

# Include chat history routes
app.include_router(chat_history_router)

# Include the mobile‐submission endpoint
app.include_router(agent_router)

# -------------------
# Middleware to Log Incoming API Requests
# -------------------
@app.middleware("http")
async def log_requests(request: Request, call_next):
    body_bytes = await request.body()
    body_text = body_bytes.decode("utf-8", errors="ignore")
    logger.info(f"Incoming request: {request.method} {request.url} - Body: {body_text}")

    # Restore request body for downstream handlers
    request._receive = lambda: {"type": "http.request", "body": body_bytes, "more_body": False}
    response = await call_next(request)
    return response

# -------------------
# CORS Middleware
# -------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3006",
        "https://localhost:3006",
        "http://127.0.0.1:3006",
        "https://127.0.0.1:3006",
        "http://localhost:3000",
        "https://localhost:3000",
        "http://127.0.0.1:3000",
        "https://127.0.0.1:3000",
        "*"  # Allow all origins for development
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# -------------------
# WebSocket Route
# -------------------
@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    logger.info(f"🔌 WebSocket connection attempt from: {websocket.client.host}:{websocket.client.port}")
    try:
        await websocket.accept()
        logger.info(f"✅ WebSocket connection accepted from: {websocket.client.host}:{websocket.client.port}")
        await chat_endpoint(websocket)  # Call the chat handler
    except Exception as e:
        error_logger.error(f"❌ WebSocket error: {e}", exc_info=True)
        if websocket.client_state.value != "disconnected":
            await websocket.close(code=1000, reason="Internal error")
    finally:
        logger.info(f"🔌 WebSocket connection closed for: {websocket.client.host}:{websocket.client.port}")

# -------------------
# Include Routers
# -------------------
# Authentication API Router (from auth_router.py)
app.include_router(auth_router)

# Feedback Router
app.include_router(feedback_router)

# Admin Dashboard Router
app.include_router(admin_router)

# Guest Info Router
app.include_router(guest_router)

# Analytics Router
app.include_router(analytics_router, prefix="/analytics")

# -------------------
# Serve React App Static Files
# -------------------
app.mount("/static", StaticFiles(directory="build/static"), name="static")

# -------------------
# SSL Configuration and Server Startup
# -------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=9006,
        ssl_keyfile="../ssl/key.pem",
        ssl_certfile="../ssl/cert.pem"
    )
