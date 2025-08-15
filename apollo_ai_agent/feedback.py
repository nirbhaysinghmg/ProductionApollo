from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from db_functions import save_user_feedback

feedback_router = APIRouter(prefix="/api", tags=["Feedback"])

class FeedbackRequest(BaseModel):
    user_id: str
    name: Optional[str] = None
    mobile: Optional[str] = None
    feedback_type: Optional[str] = None
    rating: float
    user_input: Optional[str] = None
    response: Optional[str] = None
    comment: Optional[str] = None

@feedback_router.post("/feedback")
async def submit_feedback(feedback: FeedbackRequest):
    """
    Endpoint to submit user feedback.
    Returns a JSON response indicating success or failure.
    """
    success = save_user_feedback(
        feedback.user_id,
        feedback.name,
        feedback.mobile,
        feedback.feedback_type,
        feedback.rating,
        feedback.user_input,
        feedback.response,
        feedback.comment
    )
    if success:
        return {"success": True, "message": "Thank you for providing your valuable feedback."}
    else:
        raise HTTPException(status_code=500, detail="Failed to save feedback.")
