# services/test_service.py

import uuid
import json
from typing import Dict
from models.test import (
    GenerateTestRequest, GenerateTestResponse,
    EvaluateTestRequest, EvaluateTestResponse,
    Question
)
from client.redis_client import redis_client
from graph.graph import build_state_graph

async def generate_test(req: GenerateTestRequest) -> GenerateTestResponse:
    test_id = uuid.uuid4()

    # 1) Строим и компилируем граф
    builder = build_state_graph()
    compiled_graph = builder.compile()                          # :contentReference[oaicite:0]{index=0}

    # 2) Запускаем его — асинхронно
    result_state = await compiled_graph.ainvoke({"topic": req.topic})  # :contentReference[oaicite:1]{index=1}

    # 3) Парсим и сохраняем
    questions_txt = result_state["questions"]
    questions = [Question(id=i+1, text=q) for i, q in enumerate(questions_txt)]
    redis_client.set(f"test:{test_id}", json.dumps({"questions": questions_txt}))

    return GenerateTestResponse(test_id=test_id, questions=questions)


async def evaluate_test(req: EvaluateTestRequest) -> EvaluateTestResponse:
    raw = redis_client.get(f"test:{req.test_id}")
    if not raw:
        raise ValueError("Test ID not found")
    data = json.loads(raw)
    questions_txt = data["questions"]

    answers_map = {a.question_id: a.answer for a in req.answers}
    answers = [answers_map[i+1] for i in range(len(questions_txt))]

    # 1) Строим и компилируем граф заново
    builder = build_state_graph()
    compiled_graph = builder.compile()                          # :contentReference[oaicite:2]{index=2}

    # 2) Запускаем проверку
    result_state = await compiled_graph.ainvoke({
        "questions": questions_txt,
        "answers": answers
    })                                                          # :contentReference[oaicite:3]{index=3}

    score = result_state["score"]
    total = len(questions_txt)
    correct = int(score * total)
    feedback = result_state["feedback"]
    user_message = f"Вы набрали {score*100:.0f}% правильных ответов."

    return EvaluateTestResponse(
        score=score,
        correct_count=correct,
        total_questions=total,
        feedback=feedback,
        user_message=user_message
    )
