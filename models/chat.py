from pydantic import BaseModel

class ChatStreamRequest(BaseModel):
    user_id: str
    prompt: str
