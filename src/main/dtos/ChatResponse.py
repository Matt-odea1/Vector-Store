"""
DTO for chat response payload.
"""
from pydantic import BaseModel

class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    answer: str
    context_ids: list[str] = []
    tokens_input: int | None = None
    tokens_output: int | None = None
    model_id: str | None = None
"""
DTO for chat request payload.
"""

