"""
DTOs for evaluation responses.
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any


class EvaluationJobResponse(BaseModel):
    """Initial response when evaluation job starts."""
    ok: bool
    job_id: str
    status: str  # "processing"
    message: str
    student_name: str
    total_questions: int
    estimated_time_seconds: int


class EvaluationProgress(BaseModel):
    """Progress information for ongoing evaluation."""
    questions_evaluated: int
    total_questions: int
    percentage: float


class EvaluationResult(BaseModel):
    """Final evaluation result."""
    ok: bool
    student_name: str
    total_questions: int
    total_score: float  # Out of max_score (usually 80 for 8 questions)
    max_score: float
    percentage: float
    grade: str  # Excellent/Competent/Developing/Unsatisfactory
    
    # File paths
    detailed_json_path: str
    summary_csv_path: str
    report_path: str
    
    # Average scores per criterion
    correctness_avg: float
    understanding_avg: float
    
    tokens_used: Optional[int] = None


class EvaluationStatusResponse(BaseModel):
    """Response for status checks."""
    job_id: str
    status: str  # "processing", "completed", "failed"
    progress: Optional[EvaluationProgress] = None
    result: Optional[EvaluationResult] = None
    error: Optional[str] = None
    message: str
