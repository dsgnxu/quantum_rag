#!/usr/bin/env python3
"""Задание 7: автоматическая оценка RAG на golden set.

  python scripts/prepare_gaps.py apply
  python scripts/build_index.py
  python scripts/evaluate.py

Пишет:
  logs/eval_results.jsonl
  logs/eval_results.csv
  logs/queries.jsonl   (через ask)
  docs/coverage_report.md
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.rag import ask

GOLDEN_PATH = ROOT / "golden_questions.txt"
OUT_JSONL = ROOT / "logs" / "eval_results.jsonl"
OUT_CSV = ROOT / "logs" / "eval_results.csv"
REPORT = ROOT / "docs" / "coverage_report.md"


def load_golden(path: Path) -> list[dict]:
    items = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split("|")]
        expect = parts[0].replace("expect=", "").strip()
        question = parts[1]
        keywords = (
            [k.strip().lower() for k in parts[2].split(",") if k.strip()]
            if len(parts) > 2 and parts[2]
            else []
        )
        items.append({"expect": expect, "question": question, "keywords": keywords})
    return items


def judge(item: dict, answer: str, success: bool) -> dict:
    expect = item["expect"]
    low = answer.lower()
    has_idk = "я не знаю" in low
    kw_hit = any(k in low for k in item["keywords"]) if item["keywords"] else True

    if expect == "yes":
        ok = success and not has_idk and kw_hit
        reason = "answered with keywords" if ok else "expected answer missing"
    elif expect == "no":
        ok = has_idk or not success
        reason = "correctly unknown" if ok else "hallucinated / leaked gap"
    else:
        ok = False
        reason = f"unknown expect={expect}"
    return {"ok": ok, "reason": reason}


def main() -> None:
    items = load_golden(GOLDEN_PATH)
    OUT_JSONL.parent.mkdir(parents=True, exist_ok=True)
    rows = []

    with OUT_JSONL.open("w", encoding="utf-8") as jf:
        for item in items:
            result = ask(item["question"], log=True)
            verdict = judge(item, result.answer, result.success)
            row = {
                "query": item["question"],
                "expect": item["expect"],
                "result": "success" if result.success else "unknown",
                "status": "pass" if verdict["ok"] else "fail",
                "reason": verdict["reason"],
                "chunks_found": result.chunks_found,
                "answer_length": len(result.answer),
                "sources": result.sources,
                "ok": verdict["ok"],
                "answer": result.answer,
            }
            jf.write(json.dumps(row, ensure_ascii=False) + "\n")
            rows.append(row)

    with OUT_CSV.open("w", encoding="utf-8", newline="") as cf:
        writer = csv.DictWriter(
            cf,
            fieldnames=[
                "query",
                "result",
                "sources",
                "answer_length",
                "status",
                "expect",
                "reason",
                "chunks_found",
            ],
        )
        writer.writeheader()
        for r in rows:
            writer.writerow(
                {
                    "query": r["query"],
                    "result": r["result"],
                    "sources": ";".join(r["sources"]),
                    "answer_length": r["answer_length"],
                    "status": r["status"],
                    "expect": r["expect"],
                    "reason": r["reason"],
                    "chunks_found": r["chunks_found"],
                }
            )

    total = len(rows)
    passed = sum(1 for r in rows if r["ok"])
    gap_questions = [r for r in rows if r["expect"] == "no"]
    gap_ok = sum(1 for r in gap_questions if r["ok"])
    failed = [r for r in rows if not r["ok"]]
    weak_topics = [r["query"] for r in gap_questions]

    report = f"""# Отчёт о покрытии базы знаний (Задание 7)

## Сводка
- Всего golden-вопросов: **{total}**
- Успешно по ожиданию: **{passed}/{total}**
- Вопросов на пробелы (expect=no): **{len(gap_questions)}**
- Корректных отказов на пробелах: **{gap_ok}/{len(gap_questions)}**
- Выявленных тематических пробелов: **{len(weak_topics)}**

## Искусственные пробелы
Удалены сущности: **Void Core**, **Xarn Velgor**, **Synth Flux**  
(`python scripts/prepare_gaps.py apply`).

## Темы, где бот «слеп» / должен отвечать «не знаю»
"""
    for q in weak_topics:
        report += f"- {q}\n"

    report += "\n## Ошибки / неожиданное поведение\n"
    if not failed:
        report += "- Нет — все ожидания golden set выполнены.\n"
    else:
        for r in failed:
            report += f"- [{r['expect']}] {r['query']} → {r['reason']}\n"

    report += """
## Где нерелевантные источники
Смотрите поле `sources` в `logs/eval_results.csv`. Если при expect=yes источники
не совпадают с темой вопроса — нужно улучшить чанкинг или порог `MIN_SCORE`.

## Рекомендации для QuantumForge Software
1. Назначить CODEOWNERS на каждую сущность базы знаний.
2. После major-release гонять `evaluate.py` в CI: падение coverage блокирует деплой индекса.
3. Закрывать пробелы документами по темам из expect=no, которые важны бизнесу.
4. Убирать перекрёстные упоминания удалённых сущностей (как в `prepare_gaps.py`), иначе RAG «протекает».
5. Хранить `logs/queries.jsonl` для SOC 2 / аудита источников ответов.
"""
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(report, encoding="utf-8")
    print(report)
    print(f"\nSaved: {OUT_JSONL}, {OUT_CSV}, {REPORT}")


if __name__ == "__main__":
    main()
