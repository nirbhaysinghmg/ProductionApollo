from fastapi import APIRouter, HTTPException
from db_functions import load_chat_history_from_db, clear_chat_history_from_db

chat_history_router = APIRouter(prefix="/api")

@chat_history_router.get("/chat-history")
async def get_chat_history(user_id: str):
    """Retrieve chat history for a given user."""
    history = load_chat_history_from_db(user_id)
    chat_history = [{"role": row["role"], "text": row["message"]} for row in history]
    return {"success": True, "chatHistory": chat_history}

@chat_history_router.delete("/clear-chat-history")
async def clear_chat_history(user_id: str):
    """
    Clear the chat history for a given user.
    Example call: DELETE /api/clear-chat-history?user_id=hoodarakesh@gmail.com
    """
    success = clear_chat_history_from_db(user_id)
    if success:
        return {"success": True, "message": "Chat history cleared."}
    else:
        raise HTTPException(status_code=500, detail="Failed to clear chat history.")
