
import os
from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="gemma3:12b",      # или ваша модель
    base_url="http://localhost:11434",
)
