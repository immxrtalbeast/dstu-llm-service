# graph/nodes.py
import re
import json
from typing import TypedDict, List, Any
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage
from client.ollama_client import llm

# Определяем TypedDict для промежуточного состояния:
class State(TypedDict, total=False):
    text: str
    test: Any       # будем класть сюда dict
    answers: List[str]

def generate_test(state: State) -> State:


    prompt = PromptTemplate(
        input_variables=["text"],
        template="""Create a multiple choice test with 3 questions...
                    Make it in a raw JSON struct... 
                    For each question provide 4 options (A, B, C, D) and do not mark answers...Here is the topics and difficulty : {text} \n\nTest:"""
    )
    msg = HumanMessage(content=prompt.format(text=state["text"]))
    raw = llm.invoke([msg]).content.strip()
    # Парсим JSON из ответа
   
    cleaned = re.sub(r"```json|```", "", raw).strip()
    cleaned_json = json.loads(cleaned)
    print(json.dumps(cleaned_json, indent=2))
    state["test"] = normalize_test(cleaned_json)
    return state

def resolve_test(state: State) -> State:

    prompt = PromptTemplate(
        input_variables=["test"],
        template="""Solve this test by selecting only the LETTER... 
                    Use EXACTLY this answer format: 'X, Y, Z'...\n\n{test}\n\nAnswers:"""
    )
    msg = HumanMessage(content=prompt.format(test=json.dumps(state["test"])))
    raw = llm.invoke([msg]).content.strip().split(", ")
    print(raw)
    state["answers"] = raw
    return state


def normalize_test(raw_test: dict) -> dict:
    return {
        "test_title": raw_test.get("test_name", ""),
        "questions": [
            {
                "text": q["questionText"],
                "options": [
                    {
                        "label": label,
                        "text": text
                    } for label, text in q["options"].items()
                ]
            }
            for q in raw_test["questions"]
        ]
    }
