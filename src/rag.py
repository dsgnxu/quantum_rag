from __future__ import annotations

import re
from dataclasses import dataclass

from src.config import MIN_SCORE, TOP_K
from src.indexing import search
from src.llm import generate
from src.logging_utils import append_query_log
from src.prompts import build_prompt

ENTITY_RE = re.compile(r"\b[A-Z][A-Za-z0-9\-]{2,}\b")


def _entities(text: str) -> set[str]:
    return {m.group(0).lower() for m in ENTITY_RE.finditer(text or "")}


def _chunks_support_entities(question: str, chunks: list[dict]) -> bool:
    ents = {e for e in _entities(question) if len(e) >= 4}
    if not ents:
        return True
    blob = " ".join(c.get("text", "") for c in chunks).lower()
    # все токены сущности должны встретиться (иначе семантический «шум»)
    return all(e in blob for e in ents)


@dataclass
class RagResult:
    answer: str
    sources: list[str]
    chunks_found: bool
    success: bool
    retrieved: list[dict]


def ask(
    question: str,
    top_k: int = TOP_K,
    min_score: float = MIN_SCORE,
    log: bool = True,
) -> RagResult:
    """RAG-пайплайн: embed → FAISS → prompt (few-shot + CoT) → ответ + лог."""
    retrieved = search(question, top_k=top_k)
    retrieved = [c for c in retrieved if c.get("score", 0) >= min_score]

    if retrieved and not _chunks_support_entities(question, retrieved):
        retrieved = []

    if not retrieved:
        answer = (
            "1. Ищу информацию в векторном индексе.\n"
            "2. Релевантных фрагментов нет.\n"
            "3. Итоговый ответ: Я не знаю."
        )
        result = RagResult(
            answer=answer,
            sources=[],
            chunks_found=False,
            success=False,
            retrieved=[],
        )
        if log:
            _log(question, result)
        return result

    prompt = build_prompt(question, retrieved, secure=True)
    answer = generate(prompt, question, retrieved)
    success = "я не знаю" not in answer.lower()
    result = RagResult(
        answer=answer,
        sources=[c.get("source", "") for c in retrieved],
        chunks_found=True,
        success=success,
        retrieved=retrieved,
    )
    if log:
        _log(question, result)
    return result


def _log(question: str, result: RagResult) -> None:
    append_query_log(
        {
            "query": question,
            "chunks_found": result.chunks_found,
            "answer_length": len(result.answer),
            "success": result.success,
            "sources": result.sources,
            "answer_preview": result.answer[:300],
        }
    )
