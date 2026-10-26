#!/usr/bin/env python3
"""Задание 7: искусственные пробелы в базе знаний.

Удаляет ключевые сущности:
  - void_core.md  (Void Core)
  - xarn_velgor.md (Xarn Velgor)
  - synth_flux.md (Synth Flux)

И затирает их упоминания в остальных файлах (бэкап в knowledge_base_gaps/),
чтобы бот не отвечал по перекрёстным ссылкам.

  python scripts/prepare_gaps.py apply
  python scripts/build_index.py
  python scripts/evaluate.py

  python scripts/prepare_gaps.py restore
  python scripts/build_index.py
"""

from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KB = ROOT / "knowledge_base"
GAPS = ROOT / "knowledge_base_gaps"
BACKUP = GAPS / "backup_others"

GAP_FILES = ["void_core.md", "xarn_velgor.md", "synth_flux.md"]
# длинные фразы первыми
REDACT_TERMS = [
    "Xarn Velgor",
    "Void Core",
    "Synth Flux",
]


def _redact(text: str) -> str:
    out = text
    for term in REDACT_TERMS:
        out = re.sub(re.escape(term), "[GAP]", out, flags=re.IGNORECASE)
    return out


def apply_gaps() -> None:
    GAPS.mkdir(parents=True, exist_ok=True)
    BACKUP.mkdir(parents=True, exist_ok=True)

    for name in GAP_FILES:
        src = KB / name
        if src.exists():
            shutil.move(str(src), str(GAPS / name))
            print(f"moved {name} → knowledge_base_gaps/")

    for path in sorted(KB.glob("*.md")):
        if path.name.lower() == "readme.md":
            continue
        original = path.read_text(encoding="utf-8")
        redacted = _redact(original)
        if redacted != original:
            shutil.copy2(path, BACKUP / path.name)
            path.write_text(redacted, encoding="utf-8")
            print(f"redacted mentions in {path.name}")

    print("Gaps applied. Next: python scripts/build_index.py && python scripts/evaluate.py")


def restore_gaps() -> None:
    for name in GAP_FILES:
        src = GAPS / name
        if src.exists():
            shutil.move(str(src), str(KB / name))
            print(f"restored {name}")

    if BACKUP.exists():
        for path in sorted(BACKUP.glob("*.md")):
            shutil.copy2(path, KB / path.name)
            print(f"restored backup {path.name}")
        shutil.rmtree(BACKUP)

    print("Gaps restored. Next: python scripts/build_index.py")


def main() -> None:
    action = (sys.argv[1] if len(sys.argv) > 1 else "apply").lower()
    if action == "apply":
        apply_gaps()
    elif action == "restore":
        restore_gaps()
    else:
        raise SystemExit("Usage: prepare_gaps.py [apply|restore]")


if __name__ == "__main__":
    main()
