# graph/graph.py

from langgraph.graph import StateGraph, END
from .nodes import State, generate_test, resolve_test

# Объявляем граф с TypedDict (langgraph поддерживает)
workflow = StateGraph(state_schema=State)
workflow.add_node("generate_test", generate_test)
workflow.add_node("resolve_test", resolve_test)

workflow.set_entry_point("generate_test")
workflow.add_edge("generate_test", "resolve_test")
workflow.add_edge("resolve_test", END)

engine = workflow.compile()
