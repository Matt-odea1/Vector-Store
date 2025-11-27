from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    query: str
    top_k: Optional[int] = 5
    session_id: Optional[str] = None
    include_history: bool = True  # Whether to include conversation history in context
    pedagogy_mode: Optional[str] = "explanatory"  # Teaching mode: explanatory, debugging, practice
