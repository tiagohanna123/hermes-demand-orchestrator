"""
Módulo Router — Roteamento multi-projeto por keywords.

Detecta a qual projeto uma demanda pertence baseado em
palavras-chave na descrição.
"""
from __future__ import annotations

import re
from typing import NamedTuple


class ProjectRule(NamedTuple):
    """Regra de detecção de projeto."""
    name: str
    keywords: list[str]
    path: str | None = None


# Projetos conhecidos e suas keywords
PROJECTS: list[ProjectRule] = [
    ProjectRule(
        "portfolio-dev",
        ["portfolio", "tiagohanna.com", "site pessoal"],
        "~/tiago-portfolio-dev",
    ),
    ProjectRule("sarau-secreto", ["sarau", "sarau secreto", "festival"], "~/sarau-secreto"),
    ProjectRule("music-connect", ["music connect", "khem.app", "khem"], "~/music-connect"),
    ProjectRule(
        "hermes-terminal",
        ["hermes terminal", "terminal", "dashboard", "chat"],
        "~/hermes-terminal",
    ),
    ProjectRule(
        "hermes-agent-soul",
        ["hermes agent soul", "agent soul", "hermes-soul"],
        "~/projetos/hermes-agent-soul",
    ),
    ProjectRule(
        "hermes-credential",
        ["hermes credential", "credential vault", "vault"],
        "~/hermes-credential",
    ),
    ProjectRule("hermes-broker", ["hermes broker", "message broker", "fila"], "~/hermes-broker"),
    ProjectRule(
        "hermes-demand-orchestrator",
        ["orquestrador", "orchestrator", "demanda", "demand",
         "write-ahead", "cascade", "journal"],
        "~/hermes-demand-orchestrator",
    ),
]


def detect_project(description: str) -> str | None:
    """
    Detecta o projeto mais provável para uma descrição de tarefa.

    Retorna o nome do projeto ou None se não conseguir detectar.
    """
    desc_lower = description.lower()
    best_match: tuple[int, str | None] = (0, None)

    for project in PROJECTS:
        for kw in project.keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', desc_lower):
                score = len(kw)
                if score > best_match[0]:
                    best_match = (score, project.name)

    return best_match[1]
