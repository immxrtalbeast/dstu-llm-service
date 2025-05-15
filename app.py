# app.py
from fastapi.responses import StreamingResponse
from fastapi import FastAPI, HTTPException, Depends
from models.test_workflow import (
    TestWorkflowRequest, TestWorkflowResponse
)
from graph.graph import engine
from client.ollama_client import AIModel
from models.history import History, HistoryRequest
from models.chat import ChatStreamRequest
from models.test import TestRequest, SetAnswersRequest
from langchain_core.messages import HumanMessage, AIMessage
from redis.asyncio import Redis  # Асинхронный клиент
from contextlib import asynccontextmanager
from typing import Annotated
import os
from dotenv import load_dotenv
import json

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Инициализация пула подключений к Redis
    redis = await Redis.from_url(os.getenv("REDIS_URL")) #"redis://redis:6379"
    app.state.redis = redis
    yield
    # Закрытие подключения при завершении
    await redis.close()



app = FastAPI(lifespan=lifespan)

async def get_redis() -> Redis:
    return app.state.redis

ai_model = AIModel()

async def stream_response(user_id: str, message: str, redis: Redis):
    try:
        async for chunk in ai_model.process_message(redis, user_id, message):
            yield f"data: {chunk}\n\n"
    except Exception as e:
        yield f"data: [Error] {str(e)}\n\n"

@app.post("/api/test-workflow", response_model=TestWorkflowResponse)
async def run_test_workflow(req: TestRequest, redis: Annotated[Redis, Depends(get_redis)]):
    state = {"text": req.themes}

    try:
        result = engine.invoke(state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    await redis.setex(
        f"test:{req.test_id}:answers",
        86400,  # 24 часа TTL
        json.dumps(result["answers"])
    )
    return TestWorkflowResponse(**{
        "test": result["test"]
        # "answers": result["answers"]
    })


@app.get("/chat-stream/")
async def chat_stream(
    req: ChatStreamRequest,
    redis: Annotated[Redis, Depends(get_redis)]
):
    return StreamingResponse(
        stream_response(req.user_id, req.prompt, redis),
        media_type="text/event-stream"
    )
@app.get("/get_history/")
async def get_history(
    req: HistoryRequest,
    redis: Annotated[Redis, Depends(get_redis)]
):
    history = await ai_model.get_history(redis, req.user_id)
    return {"history": history}

@app.post("/set_history/")
async def set_history(
    user_id: str,
    history: History,
    redis: Annotated[Redis, Depends(get_redis)]
):
    history_list = []
    for item in history.history:
        if item.type == "human":
            history_list.append(HumanMessage(content=item.content))
        elif item.type == "ai":
            history_list.append(AIMessage(content=item.content))
    
    await ai_model.set_history(redis, user_id, history_list)
    return {"status": "History updated"}


@app.get("/clear_history/")
async def clear_history(req:HistoryRequest, redis: Annotated[Redis, Depends(get_redis)]):
    await ai_model.clear_history(redis, req.user_id)

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.get("/test-exmpl/")
async def sendEXMPL(req: TestRequest,redis: Annotated[Redis, Depends(get_redis)]):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "exmpl2.json")
    with open(file_path, 'r', encoding='utf-8') as file:
        test = json.load(file)

    await redis.setex(
        f"test:{req.test_id}:answers",
        86400,  # 24 часа TTL
        json.dumps(test["answers"])
    )
    return {"test": test["test"]}

@app.get("/test-exmpl-answers/{test_id}")
async def sendEXMPL(test_id: str,redis: Annotated[Redis, Depends(get_redis)]):
    answers_data = await redis.get(f"test:{test_id}:answers")
    answers = json.loads(answers_data)
    return {"answers": answers}
@app.post("/test/set-answers")
async def setAnswers(req: SetAnswersRequest,redis: Annotated[Redis, Depends(get_redis)]):
    await redis.setex(
        f"test:{req.test_id}:answers",
        86400,  # 24 часа TTL
        json.dumps(req.answers)
    )
    return {"status": "done"}