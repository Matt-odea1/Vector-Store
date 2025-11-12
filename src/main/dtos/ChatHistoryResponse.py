"""
DTO for chat history response.
"""
from pydantic import BaseModel
from typing import List, Optional


class ChatMessage(BaseModel):
    """Individual message in conversation history."""
    role: str  # "user" or "assistant"
    content: str
    timestamp: str
    tokens: Optional[int] = None
    context_ids: List[str] = []


class ChatHistoryResponse(BaseModel):
    """Response model for retrieving chat history."""
    session_id: str
    messages: List[ChatMessage]
    total_messages: int
    created_at: str
    last_accessed: str
    total_tokens: int
