#!/usr/bin/env python3
"""Задание 3: построение FAISS-индекса по knowledge_base/.

Сохраняет:
  index/faiss.index  — векторный индекс
  index/docs.pkl     — чанки + метаданные (source, title, chunk_index, id)
  index/meta.json    — модель, число чанков, время сборки
  index/sample_query.txt — пример запроса и найденных чанков
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.indexing import build_index, search


def main() -> None:
    meta = build_index()
    print("Index built:")
    print(json.dumps(meta, ensure_ascii=False, indent=2))

    demos = [
        "Кто такой Xarn Velgor?",
        "Что такое Void Core?",
        "Где обучался Kael Orin у Elder Myrr?",
    ]

    lines = ["# Пример запросов к FAISS-индексу (Задание 3)\n"]
    print("\nSample retrieval:")
    for q in demos:
        hits = search(q, top_k=2)
        print(f"\nQ: {q}")
        lines.append(f"## Запрос\n`{q}`\n")
        lines.append("## Найденные чанки\n")
        for h in hits:
            preview = h["text"][:200].replace("\n", " ")
            block = (
                f"- **source:** `{h['source']}`  \n"
                f"  **id:** `{h['id']}`  **chunk_index:** {h['chunk_index']}  "
                f"**score:** {h['score']:.3f}  \n"
                f"  **text:** {preview}...\n"
            )
            print(f"  - {h['source']} score={h['score']:.3f}")
            lines.append(block)

    out = ROOT / "index" / "sample_query.txt"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nSaved example → {out}")


if __name__ == "__main__":
    main()
