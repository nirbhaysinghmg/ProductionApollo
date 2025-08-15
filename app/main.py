import os
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import update_sessions_table
from .routers import chat
from . import analytics

app = FastAPI(title="Google Gen AI RAG App with ChromaDB")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3006",
        "https://localhost:3006", 
        "http://150.241.244.252:3006",
        "https://150.241.244.252:3006",
        "http://127.0.0.1:3006",
        "https://127.0.0.1:3006",
        "*"  # Allow all origins for development
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Include routers
app.include_router(chat.router, prefix="/chat", tags=["Chat"])
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])

# Initialize database schema
update_sessions_table()

@app.get("/")
async def root():
    return {"message": "API is running"}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=9006,
        ssl_keyfile="./ssl/key.pem",
        ssl_certfile="./ssl/cert.pem"
    )