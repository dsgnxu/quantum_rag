#!/usr/bin/env python3
"""Консольный RAG-бот (Задание 4). Запуск: python bot/repl.py"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.rag import ask


def main() -> None:
    print("QuantumForge RAG Bot (REPL). Пустая строка или /exit — выход.")
    print("Пайплайн: query → embedding → FAISS → few-shot+CoT prompt → ответ\n")
    while True:
        try:
            q = input("Вы: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not q or q in {"/exit", "exit", "quit"}:
            break
        result = ask(q)
        print("\nБот:\n" + result.answer)
        if result.sources:
            print("\nИсточники:", ", ".join(result.sources))
        print()


if __name__ == "__main__":
    main()
