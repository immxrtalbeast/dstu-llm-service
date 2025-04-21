from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from uuid import UUID
from models.chat import ChatRequest, ChatResponse
from models.test import (
    GenerateTestRequest, GenerateTestResponse,
    EvaluateTestRequest, EvaluateTestResponse
)
from services.chat_service import handle_chat
from services.test_service import (
    generate_test, evaluate_test
)

app = FastAPI(title="LLM Service")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/chat", response_model=ChatResponse)
async def api_chat(req: ChatRequest):
    try:
        return await handle_chat(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-test", response_model=GenerateTestResponse)
async def api_generate_test(req: GenerateTestRequest):
    return await generate_test(req)

@app.post("/api/evaluate-test", response_model=EvaluateTestResponse)
async def api_evaluate_test(req: EvaluateTestRequest):
    return await evaluate_test(req)

@app.get("/api/health")
async def health():
    return {"status": "ok"}