from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def append_jsonl(file_path: str | Path, record: dict[str, Any]) -> None:
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


