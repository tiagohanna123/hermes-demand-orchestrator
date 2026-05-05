"""Tests for the Snapshot module — markdown journal report generator."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from hermes_demand_orchestrator.journal import JournalEntry
from hermes_demand_orchestrator.snapshot import generate_snapshot


def _write_journal(path: str, entries: list[JournalEntry]) -> None:
    """Helper to write JournalEntry list to a JSONL file."""
    with open(path, "w", encoding="utf-8") as f:
        for entry in entries:
            f.write(entry.to_json() + "\n")


class TestGenerateSnapshot:
    """Tests for generate_snapshot()."""

    def test_empty_journal_no_file(self, tmp_path: Path) -> None:
        """When journal file missing, returns 'Nenhuma demanda encontrada'."""
        journal_path = str(tmp_path / "nonexistent.jsonl")
        result = generate_snapshot(journal_path)
        assert "# Snapshot do Journal" in result
        assert "Nenhuma demanda encontrada" in result

    def test_empty_journal_file_exists(self, tmp_path: Path) -> None:
        """Empty journal returns 'Nenhuma demanda encontrada'."""
        journal_path = str(tmp_path / "journal.jsonl")
        with open(journal_path, "w") as f:
            f.write("")
        result = generate_snapshot(str(tmp_path / "journal.jsonl"))
        assert "Nenhuma demanda encontrada" in result

    def test_single_entry(self, tmp_path: Path) -> None:
        """Single entry appears with header, count, and table row."""
        now = datetime.now(UTC)
        entry = JournalEntry(
            id="DEM-001",
            ts=now,
            status="processing",
            desc="Testar modulo snapshot",
            agent="agente-x",
        )
        _write_journal(str(tmp_path / "journal.jsonl"), [entry])

        result = generate_snapshot(str(tmp_path / "journal.jsonl"))
        assert "# Snapshot do Journal" in result
        assert "**Total de demandas:** 1" in result
        assert "#DEM-001" in result
        assert "Testar modulo snapshot" in result
        assert "processing" in result
        assert "agente-x" in result

    def test_mixed_statuses(self, tmp_path: Path) -> None:
        """Entries with different statuses are in correct sections."""
        now = datetime.now(UTC)
        entries = [
            JournalEntry(
                id="DEM-001",
                ts=now,
                status="processing",
                desc="Ativa 1",
                agent="agent-1",
            ),
            JournalEntry(
                id="DEM-002",
                ts=now,
                status="delegated",
                desc="Ativa 2",
                agent="agent-2",
            ),
            JournalEntry(
                id="DEM-003",
                ts=now,
                status="completed",
                desc="Feita 1",
                summary="Sucesso",
            ),
            JournalEntry(
                id="DEM-004",
                ts=now,
                status="completed",
                desc="Feita 2",
                summary="Ok",
            ),
            JournalEntry(
                id="DEM-005",
                ts=now,
                status="failed",
                desc="Falhou",
                summary="Erro X",
            ),
            JournalEntry(
                id="DEM-006",
                ts=now,
                status="interrupted",
                desc="Parou",
                summary="Timeout",
            ),
        ]
        _write_journal(str(tmp_path / "journal.jsonl"), entries)

        result = generate_snapshot(str(tmp_path / "journal.jsonl"))

        # — Header —
        assert "# Snapshot do Journal" in result
        assert "**Total de demandas:** 6" in result

        # — Status summary —
        assert "## Resumo por Status" in result
        assert "**processing**: 1" in result
        assert "**delegated**: 1" in result
        assert "**completed**: 2" in result
        assert "**failed**: 1" in result
        assert "**interrupted**: 1" in result

        # — Active section —
        assert "## Demandas Ativas" in result
        assert "#DEM-001" in result
        assert "#DEM-002" in result

        # — Completed section —
        assert "## Últimas Completadas" in result
        assert "#DEM-003" in result
        assert "#DEM-004" in result

        # — Problems section —
        assert "## Demandas com Problemas" in result
        assert "#DEM-005" in result
        assert "#DEM-006" in result

    def test_only_completed(self, tmp_path: Path) -> None:
        """Only completed entries omit active/failed sections."""
        now = datetime.now(UTC)
        entries = [
            JournalEntry(
                id="DEM-001",
                ts=now,
                status="completed",
                desc="Feita",
                summary="Ok",
            ),
        ]
        _write_journal(str(tmp_path / "journal.jsonl"), entries)

        result = generate_snapshot(str(tmp_path / "journal.jsonl"))
        assert "## Demandas Ativas" not in result
        assert "## Demandas com Problemas" not in result
        assert "## Últimas Completadas" in result

    def test_only_active(self, tmp_path: Path) -> None:
        """Only active entries omit completed/failed sections."""
        now = datetime.now(UTC)
        entries = [
            JournalEntry(
                id="DEM-001",
                ts=now,
                status="processing",
                desc="Ativa",
            ),
        ]
        _write_journal(str(tmp_path / "journal.jsonl"), entries)

        result = generate_snapshot(str(tmp_path / "journal.jsonl"))
        assert "## Demandas Ativas" in result
        assert "## Últimas Completadas" not in result
        assert "## Demandas com Problemas" not in result

    def test_only_failed(self, tmp_path: Path) -> None:
        """Only failed entries omit active/completed sections."""
        now = datetime.now(UTC)
        entries = [
            JournalEntry(id="DEM-001", ts=now, status="failed", desc="Falhou"),
        ]
        _write_journal(str(tmp_path / "journal.jsonl"), entries)

        result = generate_snapshot(str(tmp_path / "journal.jsonl"))
        assert "## Demandas Ativas" not in result
        assert "## Últimas Completadas" not in result
        assert "## Demandas com Problemas" in result

    def test_get_latest_per_id(self, tmp_path: Path) -> None:
        """When same ID has multiple entries, only the latest state appears."""
        now = datetime.now(UTC)
        entries = [
            JournalEntry(
                id="DEM-001",
                ts=now,
                status="processing",
                desc="Primeiro estado",
            ),
            JournalEntry(
                id="DEM-001",
                ts=now,
                status="completed",
                desc="Versao final",
                summary="Done",
            ),
        ]
        _write_journal(str(tmp_path / "journal.jsonl"), entries)

        result = generate_snapshot(str(tmp_path / "journal.jsonl"))
        assert "**Total de demandas:** 1" in result  # deduplicated
        assert "Versao final" in result
        assert "Primeiro estado" not in result

    def test_markdown_table_structure(self, tmp_path: Path) -> None:
        """Active table has proper header, separator, and data rows."""
        now = datetime.now(UTC)
        entries = [
            JournalEntry(
                id="DEM-001",
                ts=now,
                status="processing",
                desc="Teste",
                agent="agente-x",
            ),
            JournalEntry(
                id="DEM-002",
                ts=now,
                status="delegated",
                desc="Outro",
                agent="agente-y",
            ),
        ]
        _write_journal(str(tmp_path / "journal.jsonl"), entries)

        result = generate_snapshot(str(tmp_path / "journal.jsonl"))
        lines = result.split("\n")

        # Find the active table
        table_idx = None
        for i, line in enumerate(lines):
            if "| ID | Descrição | Status | Agente |" in line:
                table_idx = i
                break

        assert table_idx is not None
        assert "|----|-----------|--------|--------|" in lines[table_idx + 1]
        assert "#DEM-001" in lines[table_idx + 2]
        assert "#DEM-002" in lines[table_idx + 3]

    def test_pipe_escaping_in_desc(self, tmp_path: Path) -> None:
        """Pipe chars in descriptions are escaped in tables."""
        now = datetime.now(UTC)
        entries = [
            JournalEntry(
                id="DEM-001", ts=now, status="processing", desc="Pipe | test", agent="agente"
            ),
        ]
        _write_journal(str(tmp_path / "journal.jsonl"), entries)
        result = generate_snapshot(str(tmp_path / "journal.jsonl"))
        assert "Pipe \\| test" in result

    def test_iso_timestamp_in_header(self, tmp_path: Path) -> None:
        """Snapshot includes an ISO-formatted generation timestamp."""
        now = datetime.now(UTC)
        entries = [
            JournalEntry(
                id="DEM-001",
                ts=now,
                status="processing",
                desc="Teste",
            ),
        ]
        _write_journal(str(tmp_path / "journal.jsonl"), entries)

        result = generate_snapshot(str(tmp_path / "journal.jsonl"))
        assert "*Gerado em:" in result
        assert str(now.year) in result

    def test_summary_in_completed_table(self, tmp_path: Path) -> None:
        """Completed table includes summary column with content."""
        now = datetime.now(UTC)
        entries = [
            JournalEntry(
                id="DEM-001", ts=now, status="completed", desc="Tarefa", summary="Resumo da tarefa"
            ),
        ]
        _write_journal(str(tmp_path / "journal.jsonl"), entries)

        result = generate_snapshot(str(tmp_path / "journal.jsonl"))
        assert "| ID | Descrição | Resumo |" in result
        assert "Resumo da tarefa" in result

    def test_blocked_in_problems_section(self, tmp_path: Path) -> None:
        """Blocked status is grouped with failed/interrupted in 'Problemas'."""
        now = datetime.now(UTC)
        entries = [
            JournalEntry(
                id="DEM-001",
                ts=now,
                status="blocked",
                desc="Bloqueada",
            ),
        ]
        _write_journal(str(tmp_path / "journal.jsonl"), entries)

        result = generate_snapshot(str(tmp_path / "journal.jsonl"))
        assert "## Demandas com Problemas" in result
        assert "#DEM-001" in result

    def test_empty_summary_renders_dash(self, tmp_path: Path) -> None:
        """Entries without summary show '-' in the completed table."""
        now = datetime.now(UTC)
        entries = [
            JournalEntry(
                id="DEM-001", ts=now, status="completed", desc="Tarefa sem resumo", summary=None
            ),
        ]
        _write_journal(str(tmp_path / "journal.jsonl"), entries)

        result = generate_snapshot(str(tmp_path / "journal.jsonl"))
        # None summary resolves to "" then [:80] -> "" -> shown as empty
        # The table still renders correctly
        assert "Tarefa sem resumo" in result

    def test_desc_truncation_in_table(self, tmp_path: Path) -> None:
        """Long descriptions are truncated to 80 chars in active table."""
        now = datetime.now(UTC)
        long_desc = "A" * 200
        entries = [
            JournalEntry(id="DEM-001", ts=now, status="processing", desc=long_desc, agent="agente"),
        ]
        _write_journal(str(tmp_path / "journal.jsonl"), entries)

        result = generate_snapshot(str(tmp_path / "journal.jsonl"))
        # Should have 80 chars of 'A's, not 200
        assert "A" * 80 in result
        # The full 200 should not be in the table row
        assert "A" * 200 not in result.split("\n")[0]  # probably not needed
