# client/ollama_client.py
from ollama import AsyncClient

class OllamaClient:
    def __init__(self, model: str = "gemma3:1b"):
        self.model = model
        self.client = AsyncClient()

    async def chat(self, messages: list[dict[str, str]]) -> str:
        response = await self.client.chat(
            model=self.model,
            messages=messages
        )
        return response['message']['content']

    async def generate(self, prompt: str) -> str:
        response = await self.client.generate(
            model=self.model,
            prompt=prompt,
        )
        return response['response']

ollama_client = OllamaClient()
