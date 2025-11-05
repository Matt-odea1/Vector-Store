"""
ResponseEvaluationService: Evaluates student responses to programming questions.
- Loads student response CSV
- Evaluates each response using AI
- Generates detailed reports and scores
- Supports async job processing
"""
import json
import csv
import os
import threading
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

from src.main.llm.AgentCoreProvider import AgentCoreProvider
from src.main.utils.ReadPrompt import read_prompt


class ResponseEvaluationError(Exception):
    """Raised when evaluation fails."""
    pass


class ResponseEvaluationService:
    def __init__(
        self,
        agent_client: Optional[AgentCoreProvider] = None,
        base_output_dir: str = "outputs/evaluations"
    ):
        """
        Initialize the response evaluation service.
        
        Args:
            agent_client: LLM provider (defaults to AgentCoreProvider)
            base_output_dir: Base directory for evaluation outputs
        """
        self.agent_client = agent_client or AgentCoreProvider()
        self.base_output_dir = Path(base_output_dir)
        self.base_output_dir.mkdir(parents=True, exist_ok=True)
        
        # In-memory job store
        self.jobs: Dict[str, Dict[str, Any]] = {}
        
        # Load evaluation prompt
        prompt_file = Path(__file__).resolve().parents[3] / "response_evaluation_prompt.md"
        self.evaluation_prompt = read_prompt(prompt_file)
        
        print(f"[ResponseEvaluationService] Initialized with output dir: {self.base_output_dir}")

    def start_evaluation(
        self,
        student_name: str,
        responses_file_name: str
    ) -> Dict[str, Any]:
        """
        Start async evaluation of student responses.
        
        Args:
            student_name: Student identifier
            responses_file_name: Name of CSV file in outputs/questions/
            
        Returns:
            Dictionary with job_id and initial status
        """
        # Build full path to responses file
        responses_path = Path("outputs/questions") / responses_file_name
        
        if not responses_path.exists():
            raise ResponseEvaluationError(f"Responses file not found: {responses_path}")
        
        # Read CSV to get total questions
        total_questions = self._count_questions(responses_path)
        
        # Generate job ID
        timestamp = int(datetime.now().timestamp())
        job_id = f"eval_{student_name}_{timestamp}"
        
        # Initialize job
        self.jobs[job_id] = {
            "status": "processing",
            "student_name": student_name,
            "total_questions": total_questions,
            "progress": {
                "questions_evaluated": 0,
                "total_questions": total_questions,
                "percentage": 0.0
            },
            "result": None,
            "error": None,
            "started_at": datetime.now().isoformat()
        }
        
        # Start background thread
        thread = threading.Thread(
            target=self._evaluate_responses_async,
            args=(job_id, student_name, str(responses_path))
        )
        thread.daemon = True
        thread.start()
        
        print(f"[ResponseEvaluationService] Started evaluation job: {job_id}")
        
        return {
            "job_id": job_id,
            "status": "processing",
            "student_name": student_name,
            "total_questions": total_questions,
            "estimated_time_seconds": total_questions * 8  # ~8 seconds per question
        }

    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get current status of evaluation job.
        
        Args:
            job_id: The job identifier
            
        Returns:
            Dictionary with job status and results
        """
        if job_id not in self.jobs:
            raise ResponseEvaluationError(f"Job not found: {job_id}")
        
        job = self.jobs[job_id]
        
        response = {
            "job_id": job_id,
            "status": job["status"],
            "message": self._get_status_message(job)
        }
        
        if job["status"] == "processing":
            response["progress"] = job["progress"]
        elif job["status"] == "completed":
            response["result"] = job["result"]
        elif job["status"] == "failed":
            response["error"] = job["error"]
        
        return response

    def _count_questions(self, csv_path: Path) -> int:
        """Count number of questions in CSV file."""
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return sum(1 for _ in reader)

    def _evaluate_responses_async(
        self,
        job_id: str,
        student_name: str,
        responses_file_path: str
    ):
        """
        Background task that evaluates all questions.
        
        Args:
            job_id: Job identifier
            student_name: Student name
            responses_file_path: Path to responses CSV file
        """
        try:
            print(f"[Job {job_id}] Starting evaluation for {student_name}")
            
            # Read responses CSV
            responses = self._read_responses_csv(responses_file_path)
            total_questions = len(responses)
            
            # Evaluate each question
            evaluations = []
            total_correctness = 0.0
            total_understanding = 0.0
            total_score = 0.0
            
            for i, response in enumerate(responses):
                try:
                    print(f"[Job {job_id}] Evaluating question {i + 1}/{total_questions}")
                    
                    evaluation = self._evaluate_single_question(response)
                    evaluations.append(evaluation)
                    
                    total_correctness += evaluation["correctness_score"]
                    total_understanding += evaluation["understanding_score"]
                    total_score += evaluation["total_score"]
                    
                    # Update progress
                    self.jobs[job_id]["progress"] = {
                        "questions_evaluated": i + 1,
                        "total_questions": total_questions,
                        "percentage": round((i + 1) / total_questions * 100, 1)
                    }
                    
                except Exception as e:
                    print(f"[Job {job_id}] Error evaluating question {i + 1}: {e}")
                    # Add failed evaluation
                    evaluations.append({
                        "question_number": response.get("question_number", i + 1),
                        "correctness_score": 0,
                        "understanding_score": 0,
                        "total_score": 0,
                        "strengths": [],
                        "weaknesses": ["Evaluation failed"],
                        "feedback": f"Evaluation failed: {str(e)}",
                        "suggested_improvements": [],
                        "error": str(e)
                    })
            
            # Calculate averages
            correctness_avg = total_correctness / total_questions if total_questions > 0 else 0
            understanding_avg = total_understanding / total_questions if total_questions > 0 else 0
            max_score = total_questions * 10
            percentage = (total_score / max_score * 100) if max_score > 0 else 0
            
            # Determine grade
            grade = self._calculate_grade(percentage)
            
            # Generate output files
            output_dir = self.base_output_dir / student_name
            output_dir.mkdir(parents=True, exist_ok=True)
            
            json_path = self._save_detailed_json(output_dir, student_name, evaluations, responses)
            csv_path = self._save_summary_csv(output_dir, evaluations)
            report_path = self._save_report(
                output_dir, student_name, evaluations, 
                total_score, max_score, percentage, grade,
                correctness_avg, understanding_avg
            )
            
            # Mark job as completed
            self.jobs[job_id]["status"] = "completed"
            self.jobs[job_id]["result"] = {
                "ok": True,
                "student_name": student_name,
                "total_questions": total_questions,
                "total_score": round(total_score, 1),
                "max_score": max_score,
                "percentage": round(percentage, 1),
                "grade": grade,
                "detailed_json_path": str(json_path),
                "summary_csv_path": str(csv_path),
                "report_path": str(report_path),
                "correctness_avg": round(correctness_avg, 2),
                "understanding_avg": round(understanding_avg, 2),
                "tokens_used": None  # Could track this
            }
            
            print(f"[Job {job_id}] Evaluation completed. Score: {total_score}/{max_score} ({percentage:.1f}%)")
            
        except Exception as e:
            print(f"[Job {job_id}] Evaluation failed: {e}")
            self.jobs[job_id]["status"] = "failed"
            self.jobs[job_id]["error"] = str(e)

    def _read_responses_csv(self, file_path: str) -> List[Dict[str, str]]:
        """Read student responses from CSV file."""
        responses = []
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                responses.append(row)
        return responses

    def _evaluate_single_question(self, response_data: Dict[str, str]) -> Dict[str, Any]:
        """
        Evaluate a single question response.
        
        Args:
            response_data: Dictionary with question and response data
            
        Returns:
            Evaluation result dictionary
        """
        # Build evaluation prompt
        user_prompt = self._build_evaluation_prompt(response_data)
        
        messages = [
            {
                "role": "user",
                "content": [
                    {"text": self.evaluation_prompt},
                    {"text": user_prompt}
                ]
            }
        ]
        
        # Call LLM
        try:
            result = self.agent_client.chat(messages)
            response_text = result if isinstance(result, str) else result.get("text", "")
            
            # Parse JSON response
            evaluation = self._parse_evaluation_response(response_text)
            
            # Add question metadata
            evaluation["question_number"] = int(response_data.get("question_number", 0))
            evaluation["question"] = response_data.get("question", "")
            evaluation["question_type"] = response_data.get("question_type", "")
            
            return evaluation
            
        except Exception as e:
            raise ResponseEvaluationError(f"Failed to evaluate question: {e}")

    def _build_evaluation_prompt(self, response_data: Dict[str, str]) -> str:
        """Build the evaluation prompt for a single question."""
        question_type = response_data.get("question_type", "general")
        question = response_data.get("question", "")
        code_ref = response_data.get("code_reference", "")
        transcript = response_data.get("transcript", "")
        
        prompt = f"""
**Question Type:** {question_type}

**Question:**
{question}
"""
        
        if code_ref and code_ref.strip():
            prompt += f"""
**Code Reference:**
```python
{code_ref}
```
"""
        
        prompt += f"""
**Student's Answer (Transcribed):**
{transcript}

---

Evaluate this response and provide your assessment in JSON format as specified.
"""
        
        return prompt

    def _parse_evaluation_response(self, response_text: str) -> Dict[str, Any]:
        """Parse JSON evaluation from LLM response."""
        # Try to find JSON in response
        if "```json" in response_text:
            start = response_text.find("```json") + 7
            end = response_text.find("```", start)
            json_str = response_text[start:end].strip()
        elif "```" in response_text:
            start = response_text.find("```") + 3
            end = response_text.find("```", start)
            json_str = response_text[start:end].strip()
        else:
            json_str = response_text.strip()
        
        try:
            evaluation = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ResponseEvaluationError(f"Failed to parse JSON response: {e}\nResponse: {response_text[:500]}")
        
        # Validate required fields
        required_fields = ["correctness_score", "understanding_score", "total_score", "feedback"]
        for field in required_fields:
            if field not in evaluation:
                raise ResponseEvaluationError(f"Missing required field: {field}")
        
        return evaluation

    def _calculate_grade(self, percentage: float) -> str:
        """Calculate letter grade from percentage."""
        if percentage >= 80:
            return "Excellent"
        elif percentage >= 60:
            return "Competent"
        elif percentage >= 40:
            return "Developing"
        else:
            return "Unsatisfactory"

    def _save_detailed_json(
        self,
        output_dir: Path,
        student_name: str,
        evaluations: List[Dict[str, Any]],
        responses: List[Dict[str, str]]
    ) -> Path:
        """Save detailed evaluation results as JSON."""
        filepath = output_dir / "evaluation.json"
        
        data = {
            "student_name": student_name,
            "evaluation_date": datetime.now().isoformat(),
            "total_questions": len(evaluations),
            "evaluations": evaluations
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return filepath

    def _save_summary_csv(self, output_dir: Path, evaluations: List[Dict[str, Any]]) -> Path:
        """Save summary scores as CSV."""
        filepath = output_dir / "scores.csv"
        
        fieldnames = [
            'question_number', 'question_type', 'correctness_score', 
            'understanding_score', 'total_score', 'percentage', 'feedback_summary'
        ]
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for eval_data in evaluations:
                writer.writerow({
                    'question_number': eval_data.get('question_number', ''),
                    'question_type': eval_data.get('question_type', ''),
                    'correctness_score': eval_data.get('correctness_score', 0),
                    'understanding_score': eval_data.get('understanding_score', 0),
                    'total_score': eval_data.get('total_score', 0),
                    'percentage': round(eval_data.get('total_score', 0) * 10, 1),
                    'feedback_summary': eval_data.get('feedback', '')
                })
        
        return filepath

    def _save_report(
        self,
        output_dir: Path,
        student_name: str,
        evaluations: List[Dict[str, Any]],
        total_score: float,
        max_score: float,
        percentage: float,
        grade: str,
        correctness_avg: float,
        understanding_avg: float
    ) -> Path:
        """Save human-readable markdown report."""
        filepath = output_dir / "report.md"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            # Header
            f.write(f"# Oral Exam Evaluation Report\n\n")
            f.write(f"**Student:** {student_name}\n\n")
            f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Overall Grade:** {grade} ({percentage:.1f}%)\n\n")
            f.write("---\n\n")
            
            # Summary
            f.write("## Summary\n\n")
            f.write(f"- **Total Questions:** {len(evaluations)}\n")
            f.write(f"- **Total Score:** {total_score:.1f}/{max_score}\n")
            f.write(f"- **Percentage:** {percentage:.1f}%\n")
            f.write(f"- **Average Correctness:** {correctness_avg:.2f}/5\n")
            f.write(f"- **Average Understanding:** {understanding_avg:.2f}/5\n\n")
            f.write("---\n\n")
            
            # Question-by-question
            f.write("## Question-by-Question Results\n\n")
            
            for eval_data in evaluations:
                q_num = eval_data.get('question_number', '?')
                q_type = eval_data.get('question_type', 'unknown')
                question = eval_data.get('question', '')
                correctness = eval_data.get('correctness_score', 0)
                understanding = eval_data.get('understanding_score', 0)
                total = eval_data.get('total_score', 0)
                
                f.write(f"### Question {q_num} ({q_type.capitalize()}) - {total}/10 ({total * 10}%)\n\n")
                f.write(f"**Question:** {question}\n\n")
                f.write(f"**Score Breakdown:**\n")
                f.write(f"- Correctness: {correctness}/5\n")
                f.write(f"- Understanding: {understanding}/5\n")
                f.write(f"- **Total: {total}/10**\n\n")
                
                # Strengths
                strengths = eval_data.get('strengths', [])
                if strengths:
                    f.write("**Strengths:**\n")
                    for strength in strengths:
                        f.write(f"- {strength}\n")
                    f.write("\n")
                
                # Weaknesses
                weaknesses = eval_data.get('weaknesses', [])
                if weaknesses:
                    f.write("**Areas for Improvement:**\n")
                    for weakness in weaknesses:
                        f.write(f"- {weakness}\n")
                    f.write("\n")
                
                # Feedback
                feedback = eval_data.get('feedback', '')
                if feedback:
                    f.write(f"**Feedback:** {feedback}\n\n")
                
                # Suggestions
                suggestions = eval_data.get('suggested_improvements', [])
                if suggestions:
                    f.write("**Suggested Improvements:**\n")
                    for suggestion in suggestions:
                        f.write(f"- {suggestion}\n")
                    f.write("\n")
                
                f.write("---\n\n")
            
            # Overall feedback
            f.write("## Overall Performance\n\n")
            f.write(f"You scored {total_score:.1f} out of {max_score} points ({percentage:.1f}%), ")
            f.write(f"earning a grade of **{grade}**.\n\n")
            
            if percentage >= 80:
                f.write("Excellent work! You demonstrated strong technical knowledge and clear understanding.\n")
            elif percentage >= 60:
                f.write("Good job! You showed competent understanding with room for deepening your knowledge.\n")
            elif percentage >= 40:
                f.write("Your responses show developing understanding. Focus on the suggested improvements.\n")
            else:
                f.write("Your responses indicate areas needing significant improvement. Review the feedback carefully.\n")
        
        return filepath

    def _get_status_message(self, job: Dict[str, Any]) -> str:
        """Generate status message for job."""
        status = job["status"]
        
        if status == "processing":
            progress = job["progress"]
            return f"Evaluating question {progress['questions_evaluated']} of {progress['total_questions']}..."
        elif status == "completed":
            return "Evaluation completed successfully"
        elif status == "failed":
            return f"Evaluation failed: {job.get('error', 'Unknown error')}"
        else:
            return f"Status: {status}"
