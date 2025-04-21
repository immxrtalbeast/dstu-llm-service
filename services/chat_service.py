# services/chat_service.py

import uuid
import json
from datetime import datetime
from typing import List, Dict, Any
from models.chat import ChatRequest, ChatResponse
from models.common import Message
from client.ollama_client import ollama_client
from client.redis_client import redis_client

async def handle_chat(req: ChatRequest) -> ChatResponse:
    # 1. Определяем или создаём session_id
    session_id = req.session_id or uuid.uuid4()

    # 2. Собираем историю сообщений
    #    Если клиент передаёт всю историю, берём её, иначе можно было бы подгружать из Redis
    history: List[Dict[str, Any]] = [m.dict() for m in req.messages]

    # 3. Вызываем Ollama LLM
    reply_content = await ollama_client.chat(history)

    # 4. Формируем сообщение-ответ
    reply = Message(
        role="assistant",
        content=reply_content,
        # timestamp подставится автоматически из default_factory
    )
    history.append(reply.dict())

    # 5. Сохраняем обновлённую историю в Redis (по ключу session:<session_id>:messages)
    key = f"session:{session_id}:messages"
    # Сериализуем datetime в ISO-формат
    redis_client.set(
        key,
        json.dumps(history, default=lambda o: o.isoformat() if isinstance(o, datetime) else o)
    )

    # 6. Возвращаем ответ
    return ChatResponse(
        session_id=session_id,
        reply=reply
    )
