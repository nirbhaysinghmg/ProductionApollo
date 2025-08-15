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
from analytics import router as analytics_router

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
    print(f"Incoming request: {request.method} {request.url} - Body: {body_text}")

    # Restore request body for downstream handlers
    request._receive = lambda: {"type": "http.request", "body": body_bytes, "more_body": False}
    response = await call_next(request)
    return response

# -------------------
# CORS Middleware
# -------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------
# WebSocket Route
# -------------------
@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await chat_endpoint(websocket)  # Call the chat handler

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
app.include_router(analytics_router)

# -------------------
# Serve React App Static Files
# -------------------
app.mount("/static", StaticFiles(directory="build/static"), name="static")
