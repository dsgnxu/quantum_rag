#!/usr/bin/env python3
"""Задание 6: ежедневное обновление базы знаний и FAISS-индекса.

Источник: data/incoming/*.md
  — кладёте новый/изменённый .md → скрипт копирует в knowledge_base/
  — считает отпечатки файлов, при изменениях пересобирает индекс
  — пишет лог в logs/index_update.log

Запуск вручную:
  python scripts/update_index.py

Cron (каждый день в 06:00): см. scripts/crontab.example
"""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import INCOMING_DIR, INDEX_DIR, KNOWLEDGE_BASE_DIR, UPDATE_LOG_PATH
from src.indexing import build_index

STATE_PATH = INDEX_DIR / "update_state.json"


def log(message: str) -> None:
    UPDATE_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    line = f"[{ts}] {message}"
    print(line)
    with UPDATE_LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def file_fingerprint(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    h.update(str(path.stat().st_mtime_ns).encode())
    return h.hexdigest()


def load_state() -> dict:
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    return {"files": {}}


def save_state(state: dict) -> None:
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def ingest_incoming() -> list[str]:
    """Подхват новых файлов из data/incoming → knowledge_base."""
    INCOMING_DIR.mkdir(parents=True, exist_ok=True)
    KNOWLEDGE_BASE_DIR.mkdir(parents=True, exist_ok=True)
    added: list[str] = []
    for path in sorted(INCOMING_DIR.glob("*.md")):
        dest = KNOWLEDGE_BASE_DIR / path.name
        if not dest.exists() or dest.read_bytes() != path.read_bytes():
            shutil.copy2(path, dest)
            added.append(path.name)
    return added


def changed_kb_files(state: dict) -> list[str]:
    changed: list[str] = []
    current: dict[str, str] = {}
    for path in sorted(KNOWLEDGE_BASE_DIR.glob("*.md")):
        if path.name.lower() == "readme.md":
            continue
        fp = file_fingerprint(path)
        current[path.name] = fp
        if state.get("files", {}).get(path.name) != fp:
            changed.append(path.name)
    # удаление устаревших: файлы, исчезнувшие из KB, выпадают из state при save
    state["files"] = current
    return changed


def index_size_bytes() -> int:
    faiss_path = INDEX_DIR / "faiss.index"
    docs_path = INDEX_DIR / "docs.pkl"
    total = 0
    if faiss_path.exists():
        total += faiss_path.stat().st_size
    if docs_path.exists():
        total += docs_path.stat().st_size
    return total


def main() -> int:
    started = datetime.now(timezone.utc)
    log(f"update started at {started.isoformat()}")
    try:
        incoming = ingest_incoming()
        state = load_state()
        changed = changed_kb_files(state)

        if not changed and not incoming:
            save_state(state)
            finished = datetime.now(timezone.utc)
            log(
                f"no changes detected, rebuild skipped; "
                f"finished at {finished.isoformat()}, 0 errors"
            )
            return 0

        meta = build_index()
        save_state(state)
        finished = datetime.now(timezone.utc)
        size = index_size_bytes()
        # формат как в задании + детали
        log(
            f"index updated at {finished.date()}, "
            f"{len(incoming)} files added, "
            f"{len(changed)} files changed, "
            f"chunks={meta['chunk_count']}, "
            f"index_size_bytes={size}, "
            f"0 errors"
        )
        log(f"update finished at {finished.isoformat()}")
        print(json.dumps(meta, ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:  # noqa: BLE001
        log(f"ERROR: {exc}")
        log("will retry on next scheduled run (cron)")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
