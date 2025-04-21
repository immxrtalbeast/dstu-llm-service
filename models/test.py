from pydantic import BaseModel
from uuid import UUID
from typing import List

class GenerateTestRequest(BaseModel):
    topic: str
    level: str

class Question(BaseModel):
    id: int
    text: str

class GenerateTestResponse(BaseModel):
    test_id: UUID
    questions: List[Question]

class Answer(BaseModel):
    question_id: int
    answer: str

class EvaluateTestRequest(BaseModel):
    test_id: UUID
    answers: List[Answer]

class EvaluateTestResponse(BaseModel):
    score: float
    correct_count: int
    total_questions: int
    feedback: str
    user_message: str
