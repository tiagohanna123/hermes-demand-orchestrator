"""
Módulo Journal — Write-Ahead Log append-only.

Gerencia o arquivo JSONL que registra todas as demandas
antes de qualquer processamento. Append-only = O(1) sempre.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


@dataclass
class JournalEntry:
    """Uma entrada no write-ahead log."""

    id: str
    ts: datetime
    status: str
    desc: str = ""
    agent: str | None = None
    summary: str | None = None

    def to_json(self) -> str:
        d: dict[str, Any] = {
            "id": self.id,
            "ts": self.ts.isoformat(),
            "status": self.status,
        }
        if self.desc:
            d["desc"] = self.desc
        if self.agent:
            d["agent"] = self.agent
        if self.summary:
            d["summary"] = self.summary
        return json.dumps(d, ensure_ascii=False)

    @classmethod
    def from_json(cls, line: str | None) -> JournalEntry | None:
        try:
            if line is None:
                return None
            d = json.loads(line.strip())
            if not isinstance(d, dict):
                return None
            # Parse timestamp flexibly
            ts_str = d.get("ts", "")
            if ts_str.endswith("Z"):
                ts_str = ts_str[:-1] + "+00:00"
            try:
                ts = datetime.fromisoformat(ts_str)
                # Normalize: make naive datetimes timezone-aware (UTC)
                if ts.tzinfo is None:
                    ts = ts.replace(tzinfo=UTC)
            except (ValueError, TypeError):
                ts = datetime.now(UTC)

            return cls(
                id=str(d.get("id", "unknown")),
                ts=ts,
                status=str(d.get("status", "unknown")),
                desc=str(d.get("desc", "")),
                agent=str(d["agent"]) if "agent" in d else None,
                summary=str(d["summary"]) if "summary" in d else None,
            )
        except (json.JSONDecodeError, TypeError, AttributeError):
            return None


def get_journal_path(custom_path: str | None = None) -> str:
    """Retorna o caminho absoluto do journal."""
    if custom_path:
        return os.path.expanduser(custom_path)
    return os.path.expanduser("~/.hermes/demanda-journal.jsonl")


def write_entry(journal_path: str, entry: JournalEntry) -> None:
    """Append de uma entrada no journal. Append-only, O(1)."""
    path = Path(journal_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(entry.to_json() + "\n")


def read_journal(journal_path: str) -> list[JournalEntry]:
    """Lê todas as entradas do journal."""
    path = Path(journal_path)
    if not path.exists():
        return []
    entries: list[JournalEntry] = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                entry = JournalEntry.from_json(line)
                if entry:
                    entries.append(entry)
    return entries


def get_latest_per_id(entries: list[JournalEntry]) -> dict[str, JournalEntry]:
    """Retorna o estado mais recente de cada ID."""
    latest: dict[str, JournalEntry] = {}
    for e in entries:
        latest[e.id] = e
    return latest


def filter_entries(
    entries: list[JournalEntry],
    status: str | None = None,
    since: datetime | None = None,
    agent: str | None = None,
    limit: int | None = None,
) -> list[JournalEntry]:
    """Filtra entradas por critérios. Retorna as mais recentes primeiro."""
    result = list(entries)
    if status:
        statuses = status.split(",")
        result = [e for e in result if e.status in statuses]
    if since:
        result = [e for e in result if e.ts >= since]
    if agent:
        result = [e for e in result if e.agent == agent]

    result.sort(key=lambda x: x.ts, reverse=True)
    if limit:
        result = result[:limit]
    return result


def compact_journal(journal_path: str, backup: bool = True) -> int:
    """Remove entradas intermediárias, mantendo só a última de cada ID."""
    path = Path(journal_path)
    if not path.exists():
        return 0

    entries = read_journal(str(path))
    if not entries:
        return 0

    if backup:
        backup_path = path.with_suffix(".jsonl.bak")
        path.rename(backup_path)

    latest = get_latest_per_id(entries)
    # Write only latest entries, sorted by timestamp
    sorted_entries = sorted(latest.values(), key=lambda x: x.ts)
    with open(path, "w", encoding="utf-8") as f:
        for e in sorted_entries:
            f.write(e.to_json() + "\n")

    return len(entries) - len(sorted_entries)


def count_by_status(entries: list[JournalEntry]) -> dict[str, int]:
    """Conta demandas por status."""
    latest = get_latest_per_id(entries)
    counts: dict[str, int] = {}
    for e in latest.values():
        counts[e.status] = counts.get(e.status, 0) + 1
    return counts
