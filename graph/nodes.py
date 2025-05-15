import re
import json
from typing import TypedDict, List, Any
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage
from client.ollama_client import llm

class State(TypedDict, total=False):
    text: str
    test: Any
    answers: List[str]

def generate_test(state: State) -> State:
    prompt = PromptTemplate(
        input_variables=["text", "len_text"],
template="""Generate JSON test with answers for {len_text} topics. Topics: {text}
Output STRICT JSON following this structure:
{{
    "test": [
        {{
            "title": "Topic 1 Name",
            "questions": [
                {{
                    "text": "Easy: Question text...",
                    "options": [
                        {{"label":"A","text":"Option1"}},
                        {{"label":"B","text":"Option2"}},
                        {{"label":"C","text":"Option3"}},
                        {{"label":"D","text":"Option4"}}
                    ],
                    "correct": "B"
                }},
                {{
                    "text": "Medium: Question text...",
                    "options": [...],
                    "correct": "C"
                }},
                {{
                    "text": "Hard: Question text...",
                    "options": [...],
                    "correct": "A"
                }}
            ]
        }},
        // Repeat for 9 more topics
    ]
}}

RULES:
1. Generate EXACTLY {len_text} topics in 'test' array
2. Each topic must have EXACTLY 3 questions (Easy→Medium→Hard)
3. Each question must have 'correct' field with answer letter (A-D)
4. Options must have labels A-D in order
5. Use COMPACT JSON format (no whitespace)
6. Double quotes ONLY
7. No trailing commas
8. Final JSON must be valid
""")
    
    msg = HumanMessage(content=prompt.format(text=state["text"], len_text=len(state["text"])))
    raw = llm.invoke([msg]).content.strip()
    print(raw)
    # Очистка и парсинг JSON
    cleaned = re.sub(r"```json|```", "", raw).strip()

    data = json.loads(cleaned)
    print(json.dumps(data, indent=2))

    # Нормализация и разделение данных
    normalized = normalize_test(data)
    
    state["test"] = normalized["test"]
    state["answers"] = normalized["answers"]
    return state

def normalize_test(raw_test: dict) -> dict:
    test_list = raw_test.get("test", [])
    if not test_list:
        raise ValueError("Test array is empty in response")

    result_test = []
    result_answers = []

    for test_data in test_list:
        test_title = test_data.get("title", "Unnamed Test")
        questions = []
        answers = []

        for question in test_data.get("questions", []):
            if "correct" not in question:
                raise KeyError(f"Missing 'correct' in question: {question.get('text', '')}")

            answers.append(question["correct"])

            q_data = {
                "text": question["text"],
                "options": sorted(
                    [{"label": opt["label"], "text": opt["text"]} for opt in question["options"]],
                    key=lambda x: x["label"]
                )
            }
            questions.append(q_data)

        result_test.append({
            "title": test_title,
            "questions": questions
        })

        result_answers.extend(answers)

    return {
        "test": result_test,
        "answers": result_answers
    }
