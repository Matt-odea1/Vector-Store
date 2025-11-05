"""
DTO for evaluation request.
"""
from pydantic import BaseModel


class EvaluateResponsesRequest(BaseModel):
    """Request model for evaluating student responses."""
    student_name: str
    responses_file_name: str  # e.g., "john_doe_responses.csv"
