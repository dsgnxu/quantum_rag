#!/usr/bin/env python3
"""Подмена ключевых терминов по словарю terms_map.json (Задание 2).

Логика:
1. Читает JSON-словарь (ключ = исходный термин Star Wars, значение = вымышленный).
2. Сортирует ключи по убыванию длины, чтобы «Darth Vader» заменился раньше «Vader».
3. Проходит по всем .md/.txt в --src и пишет результат в --dst.

Пример:
  python scripts/replace_terms.py \\
    --src knowledge_base_raw \\
    --dst knowledge_base \\
    --map terms_map.json
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def load_map(path: Path) -> dict[str, str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return {k: v for k, v in data.items() if not k.startswith("_")}


def apply_terms(text: str, mapping: dict[str, str]) -> str:
    items = sorted(mapping.items(), key=lambda kv: len(kv[0]), reverse=True)
    result = text
    for src, dst in items:
        result = re.sub(re.escape(src), dst, result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Replace fandom terms via terms_map.json")
    parser.add_argument("--src", type=Path, required=True, help="Папка с исходными текстами")
    parser.add_argument("--dst", type=Path, required=True, help="Папка для результата")
    parser.add_argument(
        "--map",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "terms_map.json",
    )
    args = parser.parse_args()

    mapping = load_map(args.map)
    args.dst.mkdir(parents=True, exist_ok=True)

    count = 0
    for path in sorted(list(args.src.glob("*.md")) + list(args.src.glob("*.txt"))):
        out = apply_terms(path.read_text(encoding="utf-8"), mapping)
        (args.dst / path.name).write_text(out, encoding="utf-8")
        count += 1

    print(f"Replaced terms in {count} files → {args.dst}")


if __name__ == "__main__":
    main()
