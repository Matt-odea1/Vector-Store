"""
DTO for session list response.
"""
from pydantic import BaseModel
from typing import List


class SessionInfo(BaseModel):
    """Metadata about a chat session."""
    session_id: str
    message_count: int
    created_at: str
    last_accessed: str
    total_tokens: int


class SessionListResponse(BaseModel):
    """Response model for listing active sessions."""
    sessions: List[SessionInfo]
    total: int
