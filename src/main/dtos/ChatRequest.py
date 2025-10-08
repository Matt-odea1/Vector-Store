from pydantic import BaseModel

class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    query: str
    top_k: int | None = 5
    session_id: str | None = None
