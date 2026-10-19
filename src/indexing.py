from __future__ import annotations

import json
import pickle
import time
from dataclasses import asdict, dataclass
from pathlib import Path

import faiss

from src.config import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    EMBEDDING_MODEL,
    INDEX_DIR,
    KNOWLEDGE_BASE_DIR,
)
from src.embeddings import embed_texts


@dataclass
class ChunkRecord:
    id: str
    text: str
    source: str
    title: str
    chunk_index: int


def _splitter():
    """RecursiveCharacterTextSplitter (LangChain), иначе локальный fallback."""
    try:
        from langchain_text_splitters import RecursiveCharacterTextSplitter

        return RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=["\n## ", "\n# ", "\n\n", "\n", " ", ""],
        )
    except ImportError:
        try:
            from langchain.text_splitter import RecursiveCharacterTextSplitter

            return RecursiveCharacterTextSplitter(
                chunk_size=CHUNK_SIZE,
                chunk_overlap=CHUNK_OVERLAP,
                separators=["\n## ", "\n# ", "\n\n", "\n", " ", ""],
            )
        except ImportError:
            from src.chunking import split_text

            class _Fallback:
                def split_text(self, text: str) -> list[str]:
                    return split_text(text, CHUNK_SIZE, CHUNK_OVERLAP)

            return _Fallback()


def load_documents(kb_dir: Path | None = None) -> list[tuple[str, str, str]]:
    kb_dir = kb_dir or KNOWLEDGE_BASE_DIR
    docs = []
    for path in sorted(kb_dir.glob("*.md")):
        if path.name.lower() == "readme.md":
            continue
        text = path.read_text(encoding="utf-8")
        title = text.splitlines()[0].lstrip("# ").strip() if text.strip() else path.stem
        docs.append((f"knowledge_base/{path.name}", title, text))
    return docs


def split_documents(docs: list[tuple[str, str, str]]) -> list[ChunkRecord]:
    splitter = _splitter()
    chunks: list[ChunkRecord] = []
    for source, title, text in docs:
        parts = splitter.split_text(text)
        for i, part in enumerate(parts):
            chunks.append(
                ChunkRecord(
                    id=f"{Path(source).stem}::{i}",
                    text=part,
                    source=source,
                    title=title,
                    chunk_index=i,
                )
            )
    return chunks


def build_index(
    kb_dir: Path | None = None,
    index_dir: Path | None = None,
) -> dict:
    kb_dir = kb_dir or KNOWLEDGE_BASE_DIR
    index_dir = index_dir or INDEX_DIR
    index_dir.mkdir(parents=True, exist_ok=True)

    started = time.time()
    docs = load_documents(kb_dir)
    chunks = split_documents(docs)
    if not chunks:
        raise RuntimeError(f"No documents found in {kb_dir}")

    vectors = embed_texts([c.text for c in chunks])
    dim = int(vectors.shape[1])
    index = faiss.IndexFlatIP(dim)
    index.add(vectors)

    faiss.write_index(index, str(index_dir / "faiss.index"))
    with open(index_dir / "docs.pkl", "wb") as f:
        pickle.dump([asdict(c) for c in chunks], f)

    meta = {
        "embedding_model": EMBEDDING_MODEL,
        "embedding_model_url": f"https://huggingface.co/{EMBEDDING_MODEL}",
        "embedding_dim": dim,
        "chunk_count": len(chunks),
        "document_count": len(docs),
        "chunk_size": CHUNK_SIZE,
        "chunk_overlap": CHUNK_OVERLAP,
        "vector_db": "FAISS (IndexFlatIP, cosine via L2-normalized embeddings)",
        "build_seconds": round(time.time() - started, 2),
        "kb_dir": "knowledge_base/",
    }
    (index_dir / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return meta


def load_index(
    index_dir: Path | None = None,
) -> tuple[faiss.Index, list[dict], dict]:
    index_dir = index_dir or INDEX_DIR
    index = faiss.read_index(str(index_dir / "faiss.index"))
    with open(index_dir / "docs.pkl", "rb") as f:
        docs = pickle.load(f)
    meta = json.loads((index_dir / "meta.json").read_text(encoding="utf-8"))
    return index, docs, meta


def search(
    query: str,
    top_k: int = 4,
    index_dir: Path | None = None,
) -> list[dict]:
    from src.embeddings import embed_query

    index, docs, _ = load_index(index_dir)
    q = embed_query(query).reshape(1, -1)
    scores, ids = index.search(q, top_k)
    results = []
    for score, idx in zip(scores[0], ids[0]):
        if idx < 0:
            continue
        item = dict(docs[idx])
        item["score"] = float(score)
        results.append(item)
    return results


if __name__ == "__main__":
    print(json.dumps(build_index(), ensure_ascii=False, indent=2))
