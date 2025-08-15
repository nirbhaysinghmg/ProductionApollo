from pydantic import BaseModel
from typing import Optional, Dict, Any

class QueryRequest(BaseModel):
    question: str
    session_id: str = None
    user_location: Optional[Dict[str, Any]] = None