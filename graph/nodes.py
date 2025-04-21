from langgraph.graph import StateGraph
from typing import Dict, Any
from client.ollama_client import ollama_client

async def generate_test_node(state: Dict[str, Any]) -> Dict[str, Any]:
    topic = state.topic
    prompt = f"Сгенерируй 5 открытых вопросов по теме: {topic}"
    response = await ollama_client.chat([{"role": "system", "content": prompt}])
    # парсим вопросы, например разделитель '

    questions = [q.strip() for q in response.split("'") if q.strip()]
    state.questions = questions
    return state

async def evaluate_test_node(state: Dict[str, Any]) -> Dict[str, Any]:
    # Логика проверки с помощью LLM или примитивные сравнения
    answers = state['answers']
    questions = state['questions']
    # Для примера: считаем все ответы корректными
    score = len(answers) / len(questions)
    state['score'] = score
    state['feedback'] = f"Вы ответили правильно на {score * 100:.0f}% вопросов"
    return state