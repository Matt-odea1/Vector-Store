"""
DTO for chat response payload.
"""
from pydantic import BaseModel
from typing import Optional

class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    answer: Optional[str] = None
    session_id: Optional[str] = None  # Always returned (auto-generated if not provided) in successful responses
    is_new_session: bool = False  # Indicates if this is the first message in session
    history_length: int = 0  # Number of previous messages in this session
    pedagogy_mode: Optional[str] = None  # Teaching mode used for this response
    context_ids: list[str] = []
    tokens_input: int | None = None
    tokens_output: int | None = None
    model_id: str | None = None
    error: Optional[str] = None  # Present if there was an error

"""
DTO for chat request payload.
"""

