from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from .common import Message

class ChatRequest(BaseModel):
    session_id: Optional[UUID] = Field(
        None, description="ID сессии (если есть), иначе сервис создаст новый"
    )
    messages: List[Message] = Field(
        ..., description="История сообщений для продолжения диалога"
    )

class ChatResponse(BaseModel):
    session_id: UUID = Field(..., description="ID текущей сессии")
    reply: Message = Field(..., description="Сообщение-ответ от ассистента")
