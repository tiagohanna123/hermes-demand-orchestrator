"""
Módulo Snapshot — Gerador de snapshots legíveis do journal.

Produz um relatório markdown com o estado atual de todas as demandas,
agrupadas por status.
"""

from __future__ import annotations

from datetime import UTC, datetime

from hermes_demand_orchestrator.journal import (
    get_latest_per_id,
    read_journal,
)


def generate_snapshot(journal_path: str) -> str:
    """
    Gera snapshot markdown do estado atual do journal.

    Returns:
        String com o snapshot formatado em markdown.
    """
    entries = read_journal(journal_path)
    if not entries:
        return "# Snapshot do Journal\n\n*Nenhuma demanda encontrada.*\n"

    latest = get_latest_per_id(entries)
    now = datetime.now(UTC)

    lines: list[str] = []
    lines.append("# Snapshot do Journal\n")
    lines.append(f"*Gerado em: {now.isoformat()}*\n")
    lines.append(f"**Total de demandas:** {len(latest)}\n")

    # Status summary
    status_counts: dict[str, int] = {}
    for e in latest.values():
        status_counts[e.status] = status_counts.get(e.status, 0) + 1

    lines.append("## Resumo por Status\n")
    for status, count in sorted(status_counts.items()):
        lines.append(f"- **{status}**: {count}")
    lines.append("")

    # Active demands (processing, delegated)
    active = [e for e in latest.values() if e.status in ("processing", "delegated")]
    if active:
        lines.append("## Demandas Ativas\n")
        lines.append("| ID | Descrição | Status | Agente |")
        lines.append("|----|-----------|--------|--------|")
        for e in sorted(active, key=lambda x: x.ts, reverse=True):
            agent = e.agent or "-"
            desc = e.desc[:80].replace("|", "\\|")
            lines.append(f"| #{e.id} | {desc} | {e.status} | {agent} |")
        lines.append("")

    # Recent completed
    recent = [e for e in latest.values() if e.status == "completed"][:10]
    if recent:
        lines.append("## Últimas Completadas\n")
        lines.append("| ID | Descrição | Resumo |")
        lines.append("|----|-----------|--------|")
        for e in sorted(recent, key=lambda x: x.ts, reverse=True)[:10]:
            desc = e.desc[:60].replace("|", "\\|")
            summary = (e.summary or "")[:80].replace("|", "\\|")
            lines.append(f"| #{e.id} | {desc} | {summary} |")
        lines.append("")

    # Failed/interrupted
    failed = [e for e in latest.values() if e.status in ("failed", "interrupted", "blocked")]
    if failed:
        lines.append("## Demandas com Problemas\n")
        lines.append("| ID | Descrição | Status | Resumo |")
        lines.append("|----|-----------|--------|--------|")
        for e in sorted(failed, key=lambda x: x.ts, reverse=True):
            desc = e.desc[:60].replace("|", "\\|")
            summary = (e.summary or "")[:80].replace("|", "\\|")
            lines.append(f"| #{e.id} | {desc} | {e.status} | {summary} |")
        lines.append("")

    return "\n".join(lines)
