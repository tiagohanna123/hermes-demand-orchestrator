"""
Fixtures compartilhadas para testes do Hermes Demand Orchestrator.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from hermes_demand_orchestrator.journal import JournalEntry, write_entry


@pytest.fixture
def sample_entries() -> list[JournalEntry]:
    """Retorna uma lista de JournalEntry com status variados."""
    now = datetime.now(UTC)
    return [
        JournalEntry(id="001", ts=now, status="registered", desc="Criar página inicial"),
        JournalEntry(id="002", ts=now, status="processing", desc="Refatorar API"),
        JournalEntry(
            id="003", ts=now, status="completed", desc="Deploy do site", summary="Build 284KB OK"
        ),
        JournalEntry(
            id="004", ts=now, status="failed", desc="Teste de carga", summary="Timeout após 30s"
        ),
        JournalEntry(
            id="005", ts=now, status="interrupted", desc="Migração BD", summary="Gateway reiniciou"
        ),
        JournalEntry(
            id="006",
            ts=now,
            status="completed",
            desc="Ajustar CSS header",
            summary="Padding corrigido",
        ),
    ]


@pytest.fixture
def journal_file(tmp_path: Path, sample_entries: list[JournalEntry]) -> str:
    """Cria arquivo JSONL temporário com sample_entries."""
    path = str(tmp_path / "demanda-journal.jsonl")
    for entry in sample_entries:
        write_entry(path, entry)
    return path


@pytest.fixture
def multiple_entries() -> list[JournalEntry]:
    """Retorna entradas de diferentes IDs com timestamps variados."""
    base = datetime(2026, 5, 5, tzinfo=UTC)
    return [
        JournalEntry(id="010", ts=base, status="registered", desc="Task A"),
        JournalEntry(id="020", ts=base.replace(hour=1), status="processing", desc="Task B"),
        JournalEntry(
            id="030", ts=base.replace(hour=2), status="completed", desc="Task C", summary="Feito"
        ),
        JournalEntry(
            id="010",
            ts=base.replace(hour=3),
            status="completed",
            desc="Task A",
            summary="Atualizado",
        ),
    ]


@pytest.fixture
def empty_journal(tmp_path: Path) -> str:
    """Retorna caminho para journal vazio (inexistente)."""
    return str(tmp_path / "empty.jsonl")
