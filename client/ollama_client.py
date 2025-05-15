import os
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate,HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables import RunnableConfig
from redis.asyncio import Redis
import json
from collections import defaultdict
import httpx
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import compile_system_prompt
system_prompt = compile_system_prompt("")


llm = ChatOllama(
    model=os.getenv("AI_MODEL"),      # или ваша модель
    base_url=os.getenv("OLLAMA_URL"),
)
config = RunnableConfig(max_concurrency=10)
class AIModel:

    def __init__(self, model_name=os.getenv("AI_MODEL"), temperature=1, top_k=10, base_url=os.getenv("OLLAMA_URL")):
        self.model = ChatOllama(
            model=model_name,
            temperature=temperature,
            top_k=top_k,
            base_url=base_url  # Указываем URL сервера Ollama
        )
        # self.chat_history = []
        self.stop_flag = False
        self.change_counters = defaultdict(int)
        self.save_threshold = int(os.getenv("THRESHOLD"))  # Сохранять каждые 10 изменений
        self.api_url = os.getenv("PLANDSTU-GO_URL")
        self.client = httpx.AsyncClient()
        self.system_message_prompt = SystemMessagePromptTemplate.from_template(system_prompt)

    async def _serialize_message(self, message):
        return {
            "type": message.type,
            "content": message.content,
        }

    async def _deserialize_message(self, data):
        msg_type = data.get("type", "")
        if msg_type == "human":
            return HumanMessage(**data)
        elif msg_type == "ai":
            return AIMessage(**data)
        raise ValueError(f"Unknown message type: {msg_type}")

    async def _load_history(self, redis: Redis, user_id: str) -> list:
        history_data = await redis.get(f"chat:{user_id}:history")
        if not history_data:
            return []
        
        try:
            messages = json.loads(history_data)
            return [await self._deserialize_message(m) for m in messages]
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error loading history: {e}")
            return []

    async def _save_history(self, redis: Redis, user_id: str, history: list):
        try:
            serialized = [await self._serialize_message(m) for m in history]
            await redis.setex(
                f"chat:{user_id}:history",
                86400,  # 24 часа TTL
                json.dumps(serialized))
            
            self.change_counters[user_id] += 1
            if self.change_counters[user_id] >= self.save_threshold:
                success  = await self._save_history_db(user_id, serialized)
                if success:
                    self.change_counters[user_id] = 0
        except (TypeError, ValueError) as e:
            print(f"Error saving history: {e}")

    async def clear_history(self, redis:Redis, user_id:str):
        await redis.delete(f"chat:{user_id}:history")

    async def _save_history_db(self, user_id, history):
        try:
            payload = {
                "history": history,
                "user_id": user_id
            }
            response = await self.client.post(
                self.api_url + "save-history",
                json=payload,
                timeout=5.0
            )
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Error saving history to DB: {e}")
            return False
    async def process_message(self, redis: Redis, user_id: str, user_input: str):
        # Загрузка истории из Redis
        chat_history = await self._load_history(redis, user_id)
        
        # Добавление нового сообщения пользователя
        chat_history.append(HumanMessage(content=user_input))
        messages = [self.system_message_prompt] + chat_history
        # Генерация ответа
        prompt = ChatPromptTemplate.from_messages(messages).format_prompt()
        async_stream = self.model.astream(input=prompt, config=config)
        
        result = []
        async for chunk in async_stream:
            if self.stop_flag:
                await async_stream.aclose()
                self.reset_stop_flag()
                break
            result.append(chunk.content)
            yield chunk.content.replace("\n", "/n")
        
        # Сохранение обновленной истории
        if not self.stop_flag:
            full_response = ''.join(result)
            chat_history.append(AIMessage(content=full_response))
            await self._save_history(redis, user_id, chat_history)
    async def stop_response(self):
        """Устанавливает флаг остановки для текущей генерации."""
        self.stop_flag = True

    async def reset_stop_flag(self):
        """Сбрасывает флаг остановки для нового запроса."""
        self.stop_flag = False
    async def get_history(self, redis: Redis, user_id: str):
        return await self._load_history(redis, user_id)

    async def set_history(self, redis: Redis, user_id: str, new_history: list):
        await self._save_history(redis, user_id, new_history)
        return new_history