# main_agent_api.py

import os
import json
from fastapi import APIRouter, Request, HTTPException

router = APIRouter()

# Path to the JSON-lines file for storing mobile submissions
MOBILE_DATA_FILE = os.path.join(os.getcwd(), "mobile_submissions.jsonl")

@router.post("/api/mobile")
async def receive_mobile_data(request: Request):
    """
    Receive JSON payload with `phone` and `chatHistory`,
    append it as one JSON‐per‐line, and return a success status.
    """
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(MOBILE_DATA_FILE), exist_ok=True)

        # Append the record
        with open(MOBILE_DATA_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to write file: {e}")

    return {"status": "success"}
