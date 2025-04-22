# models/test_workflow.py

from pydantic import BaseModel, Field
from typing import List

class Option(BaseModel):
    label: str = Field(..., description="Буква варианта, A–D")
    text: str  = Field(..., description="Текст варианта")

class Question(BaseModel):
    text: str              = Field(..., description="Текст вопроса")
    options: List[Option]  = Field(..., description="Список вариантов")

class TestData(BaseModel):
    questions: List[Question] = Field(..., description="Список вопросов")

class TestWorkflowRequest(BaseModel):
    text: str = Field(..., description="‘topic. difficulty.’, напр. ‘OOP. Hard.’")

class TestWorkflowResponse(BaseModel):
    test: TestData        = Field(..., description="Распарсенная JSON‑структура теста")
    answers: List[str]    = Field(..., description="Список букв‑ответов, напр. ['A','C',…]")
