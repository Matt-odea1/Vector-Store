"""
DTO for question generation response.
"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class GenerateQuestionsResponse(BaseModel):
    """Response model for question generation endpoint."""
    ok: bool
    questions: List[Dict[str, Any]]
    csv_file_path: str
    json_file_path: str
    questions_count: int
    tokens_used: Optional[int] = None
