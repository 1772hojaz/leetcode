"""Local index of scaffolded problems, stored as JSON at the repo root."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
PROBLEMS_DIR = REPO_ROOT / "problems"
INDEX_PATH = REPO_ROOT / "index.json"

STATUSES = ("todo", "attempted", "solved")


@dataclass
class ProblemRecord:
    number: int
    slug: str
    title: str
    difficulty: str = "Unknown"
    tags: list = field(default_factory=list)
    language: str = "python"
    status: str = "todo"
    path: str = ""
    hints: list = field(default_factory=list)
    hints_revealed: int = 0
    created_at: str = ""
    updated_at: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_index() -> list[dict]:
    if not INDEX_PATH.exists():
        return []
    with INDEX_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_index(records: list[dict]) -> None:
    records = sorted(records, key=lambda r: r["number"])
    with INDEX_PATH.open("w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)
        f.write("\n")


def find(number: int) -> Optional[dict]:
    for r in load_index():
        if r["number"] == number:
            return r
    return None


def upsert(record: ProblemRecord) -> None:
    records = load_index()
    now = _now()
    for i, r in enumerate(records):
        if r["number"] == record.number:
            record.created_at = r.get("created_at", now)
            record.updated_at = now
            records[i] = record.to_dict()
            save_index(records)
            return
    record.created_at = now
    record.updated_at = now
    records.append(record.to_dict())
    save_index(records)


def set_status(number: int, status: str) -> bool:
    if status not in STATUSES:
        raise ValueError(f"status must be one of {STATUSES}")
    records = load_index()
    for r in records:
        if r["number"] == number:
            r["status"] = status
            r["updated_at"] = _now()
            save_index(records)
            return True
    return False


def set_hints(number: int, hints: list) -> bool:
    """Cache freshly fetched hints for a problem, without touching progress."""
    records = load_index()
    for r in records:
        if r["number"] == number:
            r["hints"] = hints
            r["updated_at"] = _now()
            save_index(records)
            return True
    return False


def reveal_next_hint(number: int) -> tuple[Optional[str], int, int]:
    """Reveal the next unseen hint for a problem.

    Returns (hint_text_or_None, revealed_count, total_count). hint_text is
    None if there are no more hints left to reveal.
    """
    records = load_index()
    for r in records:
        if r["number"] == number:
            hints = r.get("hints", [])
            revealed = r.get("hints_revealed", 0)
            if revealed >= len(hints):
                return None, revealed, len(hints)
            hint = hints[revealed]
            r["hints_revealed"] = revealed + 1
            r["updated_at"] = _now()
            save_index(records)
            return hint, revealed + 1, len(hints)
    return None, 0, 0


def reset_hints(number: int) -> bool:
    records = load_index()
    for r in records:
        if r["number"] == number:
            r["hints_revealed"] = 0
            r["updated_at"] = _now()
            save_index(records)
            return True
    return False
