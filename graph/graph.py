# graph/graph.py

from langgraph.graph import StateGraph
from pydantic import BaseModel
from typing import List, Optional
from .nodes import generate_test_node, evaluate_test_node

class TestState(BaseModel):
    # Входное поле
    topic: Optional[str] = None

    # Промежуточные/выходные поля для графа
    questions: List[str] = []
    answers: List[str] = []
    score: float = 0.0
    feedback: str = ""

def build_state_graph() -> StateGraph:
    # Передаём state_schema, чтобы StateGraph знал, что за данные ходят по графу
    graph = StateGraph(state_schema=TestState)

    # Добавляем узлы
    graph.add_node("generate_test", generate_test_node)
    graph.add_node("evaluate_test", evaluate_test_node)

    # Настраиваем точку входа и выхода
    graph.set_entry_point("generate_test")
    graph.set_finish_point("evaluate_test")

    return graph
