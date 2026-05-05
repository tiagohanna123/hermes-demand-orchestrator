"""
CLI principal do Hermes Demand Orchestrator.
Uso: hermes-orq <comando> [opcoes]
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

from hermes_demand_orchestrator.cascade import classify_task
from hermes_demand_orchestrator.journal import (
    JournalEntry,
    get_journal_path,
    read_journal,
    write_entry,
)
from hermes_demand_orchestrator.preflight import preflight_classify
from hermes_demand_orchestrator.router import detect_project
from hermes_demand_orchestrator.snapshot import generate_snapshot


def cmd_status(args: argparse.Namespace) -> None:
    """Mostra estado atual de todas as demandas."""
    entries = read_journal(get_journal_path(args.journal))
    if not entries:
        print("Nenhuma demanda encontrada.")
        return

    # Latest entry per ID
    latest: dict[str, JournalEntry] = {}
    for e in entries:
        latest[e.id] = e

    status_counts: dict[str, int] = {}
    for e in latest.values():
        status_counts[e.status] = status_counts.get(e.status, 0) + 1

    print(f"Total: {len(latest)} demandas")
    print(f"Status: {json.dumps(status_counts)}")
    print()

    # Show processing/delegated/interrupted first
    for status_filter in ("processing", "delegated", "interrupted", "failed", "blocked"):
        for e in sorted(latest.values(), key=lambda x: x.ts, reverse=True):
            if e.status == status_filter:
                summary = f" — {e.summary[:80]}" if e.summary else ""
                print(f"  #{e.id} | {e.status} | {e.desc[:100]}{summary}")


def cmd_list(args: argparse.Namespace) -> None:
    """Lista demandas com filtros."""
    entries = read_journal(get_journal_path(args.journal))
    if not entries:
        print("Nenhuma demanda encontrada.")
        return

    latest: dict[str, JournalEntry] = {}
    for e in entries:
        latest[e.id] = e

    result = sorted(latest.values(), key=lambda x: x.ts, reverse=True)

    if args.status:
        statuses = args.status.split(",")
        result = [e for e in result if e.status in statuses]
    if args.last:
        result = result[: args.last]

    for e in result:
        ts = e.ts.strftime("%d/%m %H:%M") if hasattr(e.ts, "strftime") else str(e.ts)[:16]
        summary = f" — {e.summary[:120]}" if e.summary else ""
        print(f"  #{e.id} [{ts}] {e.status:12s} | {e.desc[:100]}{summary}")


def cmd_preflight(args: argparse.Namespace) -> None:
    """Classifica uma tarefa como direct, cascade ou cascade-deep."""
    description = " ".join(args.description)
    result = preflight_classify(description)
    cascade = classify_task(description)
    project = detect_project(description)

    print(f"Tarefa: {description}")
    print(f"Preflight: {result}")
    print(f"Cascade: {cascade}")
    print(f"Projeto: {project or 'não detectado'}")


def cmd_route(args: argparse.Namespace) -> None:
    """Detecta o projeto para uma descrição de tarefa."""
    description = " ".join(args.description)
    project = detect_project(description)
    if project:
        print(f"{project}")
    else:
        print("none")
        sys.exit(1)


def cmd_register(args: argparse.Namespace) -> None:
    """Registra uma nova demanda no journal."""
    desc = " ".join(args.description)
    entry = JournalEntry(
        id=args.id or str(int(datetime.now(UTC).timestamp())),
        ts=datetime.now(UTC),
        status="registered",
        desc=desc,
        agent=args.agent,
    )
    write_entry(get_journal_path(args.journal), entry)
    print(f"Demanda #{entry.id} registrada: {desc[:80]}")


def cmd_archive(args: argparse.Namespace) -> None:
    """Arquiva demandas com status processing/delegated/interrupted/failed."""
    entries = read_journal(get_journal_path(args.journal))
    latest: dict[str, JournalEntry] = {}
    for e in entries:
        latest[e.id] = e

    stuck_statuses = {"processing", "delegated", "interrupted", "failed"}
    stuck = {k: v for k, v in latest.items() if v.status in stuck_statuses}

    if not stuck:
        print("Nenhuma demanda emperrada para arquivar.")
        return

    journal_path = get_journal_path(args.journal)
    now = datetime.now(UTC)
    for eid, entry in stuck.items():
        archived = JournalEntry(
            id=eid,
            ts=now,
            status="archived",
            desc=entry.desc,
            summary=f"Arquivada automaticamente. Motivo: {args.motivo or 'cleanup'}",
        )
        write_entry(journal_path, archived)
        print(f"  #{eid} → archived")

    print(f"\n{len(stuck)} demanda(s) arquivada(s).")


def cmd_snapshot(args: argparse.Namespace) -> None:
    """Gera snapshot legível do journal."""
    output = generate_snapshot(get_journal_path(args.journal))
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Snapshot salvo em {args.output}")
    else:
        print(output)


def cmd_search(args: argparse.Namespace) -> None:
    """Busca por texto no journal."""
    entries = read_journal(get_journal_path(args.journal))
    query = args.query.lower()

    latest: dict[str, JournalEntry] = {}
    for e in entries:
        latest[e.id] = e

    found = []
    for e in latest.values():
        if query in e.desc.lower() or (e.summary and query in e.summary.lower()):
            found.append(e)

    for e in sorted(found, key=lambda x: x.ts, reverse=True):
        ts = e.ts.strftime("%d/%m %H:%M") if hasattr(e.ts, "strftime") else str(e.ts)[:16]
        summary = f" — {e.summary[:120]}" if e.summary else ""
        print(f"  #{e.id} [{ts}] {e.status:12s} | {e.desc[:100]}{summary}")

    print(f"\n{len(found)} resultado(s).")


def cmd_shell_completion(args: argparse.Namespace) -> None:
    """Gera script de shell completion."""
    shell = args.shell
    if shell == "bash":
        print("""_hermes_orq_completions() {
    local words cword
    words=("${COMP_WORDS[@]}")
    cword=$COMP_CWORD
    case $cword in
        cmds="status list preflight route register archive snapshot search filter"
        COMPREPLY=($(compgen -W "$cmds" -- "${words[cword]}")) ;;
    esac
}
complete -F _hermes_orq_completions hermes-orq
""")
    elif shell == "zsh":
        print("""#compdef hermes-orq
_hermes_orq() {
    local state
    _arguments '1: :(status list preflight route register archive snapshot search filter)'
}
_hermes_orq
""")
    else:
        print(f"Shell '{shell}' não suportado. Use bash ou zsh.")


def cmd_filter(args: argparse.Namespace) -> None:
    """Filtra entradas do journal por timestamp."""
    entries = read_journal(get_journal_path(args.journal))
    latest: dict[str, JournalEntry] = {}
    for e in entries:
        latest[e.id] = e

    result = sorted(latest.values(), key=lambda x: x.ts, reverse=True)

    if args.since:
        since = datetime.fromisoformat(args.since)
        result = [e for e in result if e.ts >= since]
    if args.status:
        statuses = args.status.split(",")
        result = [e for e in result if e.status in statuses]

    for e in result:
        ts = e.ts.strftime("%d/%m %H:%M") if hasattr(e.ts, "strftime") else str(e.ts)[:16]
        summary = f" — {e.summary[:120]}" if e.summary else ""
        print(f"  #{e.id} [{ts}] {e.status:12s} | {e.desc[:100]}{summary}")

    print(f"\n{len(result)} resultado(s).")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Hermes Demand Orchestrator — orquestração de demandas",
    )
    parser.add_argument(
        "--journal",
        "-j",
        default="~/.hermes/demanda-journal.jsonl",
        help="Caminho do journal (default: ~/.hermes/demanda-journal.jsonl)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # status
    p_status = sub.add_parser("status", help="Estado atual de todas as demandas")
    p_status.set_defaults(func=cmd_status)

    # list
    p_list = sub.add_parser("list", help="Lista demandas com filtros")
    p_list.add_argument("--status", "-s", help="Filtrar por status (virgulado)")
    p_list.add_argument("--last", "-n", type=int, help="Últimas N demandas")
    p_list.set_defaults(func=cmd_list)

    # preflight
    p_pre = sub.add_parser("preflight", help="Classifica tarefa (direct/cascade/cascade-deep)")
    p_pre.add_argument("description", nargs="+", help="Descrição da tarefa")
    p_pre.set_defaults(func=cmd_preflight)

    # route
    p_route = sub.add_parser("route", help="Detecta projeto para uma tarefa")
    p_route.add_argument("description", nargs="+", help="Descrição da tarefa")
    p_route.set_defaults(func=cmd_route)

    # register
    p_reg = sub.add_parser("register", help="Registra nova demanda")
    p_reg.add_argument("description", nargs="+", help="Descrição da demanda")
    p_reg.add_argument("--id", help="ID customizado (default: timestamp)")
    p_reg.add_argument("--agent", help="Agente responsável")
    p_reg.set_defaults(func=cmd_register)

    # archive
    p_arch = sub.add_parser("archive", help="Arquiva demandas emperradas")
    p_arch.add_argument("--motivo", "-m", default="cleanup", help="Motivo do arquivamento")
    p_arch.set_defaults(func=cmd_archive)

    # snapshot
    p_snap = sub.add_parser("snapshot", help="Gera snapshot legível do journal")
    p_snap.add_argument("--output", "-o", help="Arquivo de saída (default: stdout)")
    p_snap.set_defaults(func=cmd_snapshot)

    # search
    p_search = sub.add_parser("search", help="Busca por texto no journal")
    p_search.add_argument("query", help="Texto para buscar")
    p_search.set_defaults(func=cmd_search)

    # shell-completion
    p_comp = sub.add_parser("shell-completion", help="Gera script de shell completion")
    p_comp.add_argument("shell", choices=["bash", "zsh"], help="Shell alvo")
    p_comp.set_defaults(func=cmd_shell_completion)

    # filter
    p_filter = sub.add_parser("filter", help="Filtra entradas por timestamp/status")
    p_filter.add_argument("--since", help="A partir de (ISO 8601)")
    p_filter.add_argument("--status", "-s", help="Filtrar por status (virgulado)")
    p_filter.set_defaults(func=cmd_filter)

    parsed = parser.parse_args(argv)
    parsed.func(parsed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
