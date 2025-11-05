"""
DTO for question generation request.
"""
from pydantic import BaseModel


class GenerateQuestionsRequest(BaseModel):
    """Request model for generating questions from assignment and student code."""
    assignment_brief: str
    student_code: str
    student_name: str
