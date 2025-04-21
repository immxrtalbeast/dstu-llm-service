from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal
from uuid import UUID

class Message(BaseModel):
    role: Literal['system', 'user', 'assistant'] = Field(
        ..., description="Роль автора сообщения"
    )
    content: str = Field(..., description="Текст сообщения")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Время создания сообщения (UTC)"
    )

class HealthResponse(BaseModel):
    status: Literal['ok', 'error'] = Field(..., description="Статус сервиса")

class UUIDResponse(BaseModel):
    id: UUID = Field(..., description="Универсальный идентификатор")
