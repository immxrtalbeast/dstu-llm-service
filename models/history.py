from pydantic import BaseModel
from typing import List, Optional

class HistoryItem(BaseModel):
    content: str
    additional_kwargs: dict
    response_metadata: dict
    type: str
    name: Optional[str] = None
    id: Optional[str] = None
    example: bool
    tool_calls: Optional[List] = None
    invalid_tool_calls: Optional[List] = None
    usage_metadata: Optional[dict] = None


class History(BaseModel):
    history: List[HistoryItem]


class HistoryRequest(BaseModel):
    user_id: str

