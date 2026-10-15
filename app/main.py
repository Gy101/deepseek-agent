"""FastAPI 应用入口。"""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .agent import Agent
from .config import BASE_DIR, settings
from .deepseek_client import DeepSeekClient, DeepSeekError
from .rag.store import KnowledgeStore
from .schemas import ChatRequest, ChatResponse

STATIC_DIR = BASE_DIR / "static"
KNOWLEDGE_DIR = (BASE_DIR / settings.knowledge_dir).resolve()

store = KnowledgeStore(KNOWLEDGE_DIR)
client = DeepSeekClient()
agent = Agent(store, client)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    store.build()
    yield
    client.close()


app = FastAPI(title="DeepSeek Agent", version="0.1.0", lifespan=lifespan)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "chunks": store.chunk_count}


@app.post("/ingest")
def ingest() -> dict:
    store.build()
    return {"status": "ok", "chunks": store.chunk_count}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    history = [{"role": m.role, "content": m.content} for m in req.history]
    try:
        result = agent.chat(req.message, history)
    except DeepSeekError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e
    return ChatResponse(**result)


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")
