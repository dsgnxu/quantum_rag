from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from src.config import QUERY_LOG_PATH


def append_query_log(record: dict, path: Path | None = None) -> None:
    """Лог запросов к боту (Задание 7): JSONL."""
    path = path or QUERY_LOG_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **record,
    }
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
