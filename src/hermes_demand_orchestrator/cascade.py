"""
Módulo Cascade — Lógica de decisão para Swarm Cascade.

Determina se uma tarefa deve ser executada diretamente,
via cascade simples ou cascade profunda com subagentes.
"""

from __future__ import annotations

from typing import Literal

CascadeDecision = Literal["direct", "cascade", "cascade-deep"]

# Keywords that trigger cascade
CASCADE_WORDS = {
    "deploy",
    "build",
    "test",
    "refatorar",
    "criar",
    "feature",
    "migrar",
    "configurar",
    "implementar",
    "instalar",
    "publicar",
    "release",
}

# Keywords that trigger direct execution
DIRECT_WORDS = {
    "listar",
    "mostrar",
    "ver",
    "status",
    "ler",
    "buscar",
    "contar",
    "qual",
    "como",
    "quem",
    "onde",
    "quando",
    "ajustar",
    "mudar",
    "editar",
    "corrigir",
    "typo",
    "remover",
    "css",
    "padding",
}

# Words that make cascade deeper
DEEP_WORDS = {"deploy", "test", "refatorar"}


def classify_task(description: str) -> CascadeDecision:
    """
    Classifica uma tarefa baseado na descrição.

    >>> classify_task("listar usuarios")
    'direct'
    >>> classify_task("fazer deploy do site")
    'cascade'
    >>> classify_task("deploy do site com testes")
    'cascade-deep'
    """
    words = set(description.lower().split())

    # Direct keywords win
    if words & DIRECT_WORDS:
        return "direct"

    # Cascade deep: 2+ deep words
    deep_count = len(words & DEEP_WORDS)
    if deep_count >= 2:
        return "cascade-deep"

    # Cascade: 1+ cascade words
    if words & CASCADE_WORDS:
        return "cascade"

    return "direct"
