from pydantic import BaseModel
from typing import List


class TestRequest(BaseModel):
    test_id: str
    themes: List[str]

class SetAnswersRequest(BaseModel):
    test_id: str
    answers: List[str]