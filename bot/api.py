#!/usr/bin/env python3
"""Опциональный REST-интерфейс: uvicorn bot.api:app --port 8000"""

from __future__ import annotations

import sys
from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.rag import ask

app = FastAPI(title="QuantumForge RAG Bot", version="1.0.0")


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1)
    top_k: int = 4


class AskResponse(BaseModel):
    answer: str
    sources: list[str]
    chunks_found: bool
    success: bool


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
def ask_endpoint(body: AskRequest) -> AskResponse:
    result = ask(body.question, top_k=body.top_k)
    return AskResponse(
        answer=result.answer,
        sources=result.sources,
        chunks_found=result.chunks_found,
        success=result.success,
    )
