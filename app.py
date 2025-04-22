# app.py

from fastapi import FastAPI, HTTPException
from models.test_workflow import (
    TestWorkflowRequest, TestWorkflowResponse
)
from graph.graph import engine

app = FastAPI(title="Test Workflow Service")

@app.post("/api/test-workflow", response_model=TestWorkflowResponse)
def run_test_workflow(req: TestWorkflowRequest):
    # 1) инициализируем начальное состояние
    state = {"text": req.text}

    # 2) запускаем синхронный invoke (наши узлы — sync)
    try:
        result = engine.invoke(state)
    except Exception as e:
        # если что-то пошло не так — покажем в detail
        raise HTTPException(status_code=500, detail=str(e))

    # 3) вернём готовую структуру
    return TestWorkflowResponse(**{
        "test": result["test"],
        "answers": result["answers"]
    })

@app.get("/api/health")
def health():
    return {"status": "ok"}
