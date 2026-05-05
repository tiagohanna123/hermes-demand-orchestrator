"""Testes unitários do módulo journal — write-ahead log append-only.

Cobre: JournalEntry (serialização/deserialização),
write_entry / read_journal, get_latest_per_id, filter_entries,
compact_journal, count_by_status.
"""

from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone, timedelta

import pytest

from hermes_demand_orchestrator.journal import (
    JournalEntry,
    compact_journal,
    count_by_status,
    filter_entries,
    get_journal_path,
    get_latest_per_id,
    read_journal,
    write_entry,
)


# ─── Fixtures ──────────────────────────────────────────────────────────


@pytest.fixture
def journal_path(tmp_path):
    """Caminho para um arquivo de journal temporário."""
    return str(tmp_path / "test-journal.jsonl")


def _entry(
    id: str = "dem-001",
    ts: datetime | None = None,
    status: str = "pending",
    desc: str = "descricao",
    agent: str | None = None,
    summary: str | None = None,
) -> JournalEntry:
    """Helper para criar JournalEntry com timestamp default."""
    if ts is None:
        ts = datetime(2025, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
    return JournalEntry(id=id, ts=ts, status=status, desc=desc, agent=agent, summary=summary)


# ─── JournalEntry — to_json / from_json ────────────────────────────────


class TestJournalEntrySerialization:
    """Serialização e deserialização de JournalEntry."""

    def test_to_json_basic(self):
        """to_json produz JSON com campos obrigatórios."""
        e = _entry()
        data = json.loads(e.to_json())
        assert data["id"] == "dem-001"
        assert data["ts"] == "2025-06-01T12:00:00+00:00"
        assert data["status"] == "pending"
        assert data["desc"] == "descricao"

    def test_to_json_without_desc(self):
        """desc vazia é omitida do JSON."""
        e = _entry(desc="")
        data = json.loads(e.to_json())
        assert "desc" not in data

    def test_to_json_with_agent_and_summary(self):
        """agent e summary aparecem no JSON quando presentes."""
        e = _entry(agent="agent-alpha", summary="tudo ok")
        data = json.loads(e.to_json())
        assert data["agent"] == "agent-alpha"
        assert data["summary"] == "tudo ok"

    def test_to_json_without_agent_or_summary(self):
        """agent/summary None são omitidos do JSON."""
        e = _entry()
        data = json.loads(e.to_json())
        assert "agent" not in data
        assert "summary" not in data

    def test_to_json_ensure_ascii(self):
        """Caracteres não-ASCII são preservados no JSON."""
        e = _entry(desc="çãö测试")
        data = json.loads(e.to_json())
        assert data["desc"] == "çãö测试"

    def test_from_json_roundtrip(self):
        """Um entry serializado e desserializado mantém todos os campos."""
        original = _entry(
            id="dem-099",
            status="completed",
            desc="teste redondo",
            agent="bot",
            summary="sucesso",
        )
        line = original.to_json()
        restored = JournalEntry.from_json(line)
        assert restored is not None
        assert restored.id == original.id
        assert restored.ts == original.ts
        assert restored.status == original.status
        assert restored.desc == original.desc
        assert restored.agent == original.agent
        assert restored.summary == original.summary

    def test_from_json_minimal(self):
        """from_json funciona com apenas id/ts/status."""
        line = json.dumps({"id": "x", "ts": "2025-01-01T00:00:00Z", "status": "done"})
        e = JournalEntry.from_json(line)
        assert e is not None
        assert e.id == "x"
        assert e.status == "done"
        assert e.desc == ""
        assert e.agent is None
        assert e.summary is None

    def test_from_json_missing_all_fields(self):
        """Campos ausentes viram valores default."""
        line = json.dumps({"id": "x"})
        e = JournalEntry.from_json(line)
        assert e is not None
        assert e.id == "x"
        assert e.status == "unknown"
        assert e.desc == ""
        assert e.agent is None

    def test_from_json_z_suffix(self):
        """Timestamp com sufixo 'Z' é convertido corretamente."""
        line = json.dumps({"id": "1", "ts": "2025-06-01T12:00:00Z", "status": "ok"})
        e = JournalEntry.from_json(line)
        assert e is not None
        assert e.ts == datetime(2025, 6, 1, 12, 0, 0, tzinfo=timezone.utc)

    def test_from_json_invalid_ts_falls_back(self):
        """Timestamp inválido cai para datetime.now(utc)."""
        line = json.dumps({"id": "1", "ts": "nope", "status": "ok"})
        e = JournalEntry.from_json(line)
        assert e is not None
        # Deve ser aproximadamente agora
        now = datetime.now(timezone.utc)
        diff = abs((e.ts - now).total_seconds())
        assert diff < 5

    def test_from_json_invalid_json(self):
        """Linha com JSON inválido retorna None."""
        assert JournalEntry.from_json("{not json}") is None

    def test_from_json_not_dict(self):
        """JSON que não é dict retorna None."""
        assert JournalEntry.from_json('"string"') is None

    def test_from_json_empty_line(self):
        """Linha vazia retorna None."""
        assert JournalEntry.from_json("") is None

    def test_from_json_type_error(self):
        """TypeError (ex.: None) não é tratado pela função (AttributeError)."""
        with pytest.raises(AttributeError):
            JournalEntry.from_json(None)  # type: ignore[arg-type]


# ─── write_entry / read_journal ────────────────────────────────────────


class TestWriteReadJournal:
    """Escrita e leitura do arquivo journal."""

    def test_write_and_read_one(self, journal_path):
        """Escreve uma entrada e lê de volta."""
        e = _entry()
        write_entry(journal_path, e)
        entries = read_journal(journal_path)
        assert len(entries) == 1
        assert entries[0].id == "dem-001"
        assert entries[0].status == "pending"

    def test_write_and_read_multiple(self, journal_path):
        """Escreve várias entradas e lê todas."""
        for i in range(5):
            write_entry(journal_path, _entry(id=f"dem-{i:03d}"))
        entries = read_journal(journal_path)
        assert len(entries) == 5
        assert [e.id for e in entries] == [f"dem-{i:03d}" for i in range(5)]

    def test_read_journal_nonexistent(self, tmp_path):
        """Arquivo inexistente retorna lista vazia."""
        entries = read_journal(str(tmp_path / "nonexistent.jsonl"))
        assert entries == []

    def test_read_journal_skips_blank_lines(self, journal_path):
        """Linhas em branco no arquivo são ignoradas."""
        path = journal_path
        write_entry(path, _entry(id="a"))
        with open(path, "a", encoding="utf-8") as f:
            f.write("\n   \n")
        write_entry(path, _entry(id="b"))
        entries = read_journal(path)
        assert len(entries) == 2

    def test_read_journal_skips_invalid_lines(self, journal_path):
        """Linhas com JSON inválido são ignoradas."""
        path = journal_path
        write_entry(path, _entry(id="a"))
        with open(path, "a", encoding="utf-8") as f:
            f.write("{invalid}\n")
        write_entry(path, _entry(id="b"))
        entries = read_journal(path)
        assert len(entries) == 2

    def test_write_creates_parent_dir(self, tmp_path):
        """write_entry cria diretórios intermediários."""
        path = str(tmp_path / "sub" / "deep" / "journal.jsonl")
        write_entry(path, _entry())
        assert read_journal(path) != []

    def test_write_appends_not_overwrites(self, journal_path):
        """write_entry é append-only: não sobrescreve dados existentes."""
        write_entry(journal_path, _entry(id="first"))
        write_entry(journal_path, _entry(id="second"))
        entries = read_journal(journal_path)
        assert len(entries) == 2


# ─── get_journal_path ──────────────────────────────────────────────────


class TestGetJournalPath:
    """Resolução do caminho do journal."""

    def test_default_path(self):
        """Sem custom_path retorna ~/.hermes/demanda-journal.jsonl."""
        path = get_journal_path()
        assert path.endswith("/.hermes/demanda-journal.jsonl")

    def test_custom_path(self):
        """Com custom_path, retorna o caminho expandido."""
        path = get_journal_path("~/meu-journal.jsonl")
        assert path.endswith("/meu-journal.jsonl")
        assert "~" not in path

    def test_absolute_path_passthrough(self):
        """Caminho absoluto é retornado como está."""
        path = get_journal_path("/tmp/custom-journal.jsonl")
        assert path == "/tmp/custom-journal.jsonl"


# ─── get_latest_per_id ─────────────────────────────────────────────────


class TestGetLatestPerId:
    """Agrupamento por ID (última entrada de cada ID)."""

    def test_single_entry(self):
        """Uma entrada é retornada para seu ID."""
        e = _entry()
        result = get_latest_per_id([e])
        assert result == {"dem-001": e}

    def test_latest_overwrites_older(self):
        """Entrada mais recente sobrescreve a mais antiga para o mesmo ID."""
        earlier = _entry(ts=datetime(2025, 1, 1, tzinfo=timezone.utc))
        later = _entry(ts=datetime(2025, 6, 1, tzinfo=timezone.utc))
        result = get_latest_per_id([earlier, later])
        assert result["dem-001"] is later

    def test_multiple_ids(self):
        """IDs diferentes são mantidos separadamente."""
        e1 = _entry(id="a")
        e2 = _entry(id="b")
        result = get_latest_per_id([e1, e2])
        assert set(result.keys()) == {"a", "b"}

    def test_empty_list(self):
        """Lista vazia retorna dict vazio."""
        assert get_latest_per_id([]) == {}


# ─── filter_entries ────────────────────────────────────────────────────


class TestFilterEntries:
    """Filtragem de entradas por status, data, agente e limite."""

    @pytest.fixture
    def sample_entries(self):
        """Conjunto variado de entradas para testes de filtro."""
        t = datetime(2025, 6, 1, tzinfo=timezone.utc)
        return [
            _entry(id="a", ts=t + timedelta(hours=1), status="pending", agent="alpha"),
            _entry(id="b", ts=t + timedelta(hours=2), status="completed", agent="beta"),
            _entry(id="c", ts=t + timedelta(hours=3), status="failed", agent="alpha"),
            _entry(id="d", ts=t + timedelta(hours=4), status="pending", agent="gamma"),
        ]

    def test_no_filter(self, sample_entries):
        """Sem filtros, retorna todas ordenadas por ts descendente."""
        result = filter_entries(sample_entries)
        assert len(result) == 4
        assert [e.id for e in result] == ["d", "c", "b", "a"]

    def test_filter_by_status(self, sample_entries):
        """Filtra por status único."""
        result = filter_entries(sample_entries, status="pending")
        assert len(result) == 2
        assert all(e.status == "pending" for e in result)

    def test_filter_by_multiple_statuses(self, sample_entries):
        """Filtra por múltiplos status separados por vírgula."""
        result = filter_entries(sample_entries, status="completed,failed")
        assert len(result) == 2
        assert {e.id for e in result} == {"b", "c"}

    def test_filter_by_since(self, sample_entries):
        """Filtra entradas a partir de uma data."""
        t = datetime(2025, 6, 1, hour=3, tzinfo=timezone.utc)
        result = filter_entries(sample_entries, since=t)
        assert len(result) == 2
        assert {e.id for e in result} == {"c", "d"}

    def test_filter_by_agent(self, sample_entries):
        """Filtra por agente."""
        result = filter_entries(sample_entries, agent="alpha")
        assert len(result) == 2
        assert all(e.agent == "alpha" for e in result)

    def test_filter_with_limit(self, sample_entries):
        """Limita o número de resultados."""
        result = filter_entries(sample_entries, limit=2)
        assert len(result) == 2
        assert [e.id for e in result] == ["d", "c"]

    def test_filter_combined(self, sample_entries):
        """Combinação de múltiplos filtros."""
        t = datetime(2025, 6, 1, hour=1, tzinfo=timezone.utc)
        result = filter_entries(sample_entries, status="pending,failed", since=t, agent="alpha", limit=1)
        assert len(result) == 1
        assert result[0].id == "c"  # failed + alpha, mais recente

    def test_filter_empty_result(self, sample_entries):
        """Filtro que não casa nada retorna lista vazia."""
        result = filter_entries(sample_entries, status="nonexistent")
        assert result == []

    def test_filter_empty_list(self):
        """Lista vazia de entrada retorna lista vazia."""
        assert filter_entries([]) == []

    def test_since_none(self):
        """since=None não afeta o filtro."""
        e1 = _entry(id="a", ts=datetime(2024, 1, 1, tzinfo=timezone.utc))
        e2 = _entry(id="b", ts=datetime(2025, 1, 1, tzinfo=timezone.utc))
        result = filter_entries([e1, e2], since=None)
        assert len(result) == 2


# ─── compact_journal ───────────────────────────────────────────────────


class TestCompactJournal:
    """Compactação do journal — remove entradas intermediárias."""

    def test_compact_removes_duplicates(self, journal_path):
        """Compactação mantém só a última entrada de cada ID."""
        path = journal_path
        ts = datetime(2025, 6, 1, tzinfo=timezone.utc)
        write_entry(path, _entry(id="a", ts=ts, status="pending"))
        write_entry(path, _entry(id="a", ts=ts + timedelta(hours=1), status="completed"))
        write_entry(path, _entry(id="b", ts=ts, status="pending"))

        removed = compact_journal(path)
        assert removed == 1  # uma entrada de "a" foi removida

        entries = read_journal(path)
        assert len(entries) == 2
        # "a" deve estar com status "completed" (mais recente)
        a_entries = [e for e in entries if e.id == "a"]
        assert len(a_entries) == 1
        assert a_entries[0].status == "completed"

    def test_compact_no_duplicates(self, journal_path):
        """Sem duplicatas, compactação não remove nada."""
        path = journal_path
        write_entry(path, _entry(id="a"))
        write_entry(path, _entry(id="b"))

        removed = compact_journal(path)
        assert removed == 0
        assert len(read_journal(path)) == 2

    def test_compact_nonexistent_file(self, tmp_path):
        """Arquivo inexistente retorna 0."""
        path = str(tmp_path / "missing.jsonl")
        assert compact_journal(path) == 0

    def test_compact_empty_file(self, journal_path):
        """Arquivo vazio retorna 0."""
        Path(journal_path).touch()
        assert compact_journal(journal_path) == 0

    def test_compact_with_backup(self, journal_path):
        """Com backup=True, cria arquivo .bak."""
        path = journal_path
        write_entry(path, _entry(id="a", status="pending"))
        write_entry(path, _entry(id="a", status="done"))

        compact_journal(path, backup=True)

        backup_path = path + ".bak"
        assert Path(backup_path).exists()
        # Backup deve ter as 2 entradas originais
        backup_entries = read_journal(backup_path)
        assert len(backup_entries) == 2

        # Journal compactado tem 1 entrada
        assert len(read_journal(path)) == 1

    def test_compact_without_backup(self, journal_path):
        """Com backup=False, não cria .bak e compacta."""
        path = journal_path
        write_entry(path, _entry(id="a", status="pending"))
        write_entry(path, _entry(id="a", status="done"))

        compact_journal(path, backup=False)

        backup_path = path + ".bak"
        assert not Path(backup_path).exists()
        assert len(read_journal(path)) == 1

    def test_compact_removes_multiple_duplicates(self, journal_path):
        """Múltiplos IDs com várias versões cada são compactados."""
        path = journal_path
        ts = datetime(2025, 1, 1, tzinfo=timezone.utc)
        for i in range(3):
            for j in range(3):
                write_entry(path, _entry(id=f"id-{i}", ts=ts + timedelta(hours=j), status=f"v{j}"))

        # Antes: 3 IDs × 3 entradas = 9 linhas
        removed = compact_journal(path)
        assert removed == 6  # 9 - 3 = 6 removidas

        entries = read_journal(path)
        assert len(entries) == 3
        # Cada ID deve estar com a última versão
        for i in range(3):
            e = [e for e in entries if e.id == f"id-{i}"][0]
            assert e.status == "v2"


# ─── count_by_status ───────────────────────────────────────────────────


class TestCountByStatus:
    """Contagem de demandas por status (apenas últimas versões)."""

    def test_single_entry(self):
        """Uma entrada: contagem 1 para seu status."""
        e = _entry(status="pending")
        counts = count_by_status([e])
        assert counts == {"pending": 1}

    def test_multiple_entries_different_statuses(self):
        """Entradas com status diferentes são contadas separadamente."""
        entries = [
            _entry(id="a", status="pending"),
            _entry(id="b", status="completed"),
            _entry(id="c", status="pending"),
        ]
        counts = count_by_status(entries)
        assert counts == {"pending": 2, "completed": 1}

    def test_only_latest_status_counts(self):
        """Apenas a última versão de cada ID é considerada."""
        entries = [
            _entry(id="x", status="pending"),
            _entry(id="x", status="completed"),
            _entry(id="y", status="pending"),
        ]
        counts = count_by_status(entries)
        # ID "x" conta só como "completed" (último status)
        assert counts == {"completed": 1, "pending": 1}

    def test_empty_list(self):
        """Lista vazia retorna dict vazio."""
        assert count_by_status([]) == {}

    def test_all_same_status(self):
        """Todas com mesmo status."""
        entries = [_entry(id=str(i), status="running") for i in range(10)]
        counts = count_by_status(entries)
        assert counts == {"running": 10}
