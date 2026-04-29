"""
ShopMind - Agentic Retail AI
FastAPI backend with LangChain agent, FAISS RAG, and NVIDIA Nemotron
"""

from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(__file__).parent / ".env")
load_dotenv(Path(__file__).parent.parent / ".env")

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import json
import asyncio

from agent import ShopMindAgent

app = FastAPI(
    title="ShopMind API",
    description="Agentic retail AI powered by NVIDIA Nemotron + RAG",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agent once at startup
agent: ShopMindAgent = None

@app.on_event("startup")
async def startup_event():
    global agent
    agent = ShopMindAgent()
    await agent.initialize()
    print("ShopMind agent initialized.")

class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = "default"
    stream: Optional[bool] = False

class QueryResponse(BaseModel):
    answer: str
    sources: list[dict]
    products: list[dict]
    agent_steps: list[str]
    model: str
    retrieval_score: float

@app.post("/api/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    try:
        result = await agent.run(request.query, session_id=request.session_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/query/stream")
async def query_stream(request: QueryRequest):
    """Streaming endpoint — yields agent steps + final answer as SSE"""
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    async def event_generator():
        async for chunk in agent.run_stream(request.query, session_id=request.session_id):
            yield f"data: {json.dumps(chunk)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/api/health")
async def health():
    return {"status": "ok", "agent_ready": agent is not None}

@app.delete("/api/session/{session_id}")
async def clear_session(session_id: str):
    if agent:
        agent.clear_session(session_id)
    return {"cleared": session_id}
