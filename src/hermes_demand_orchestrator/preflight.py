"""
Módulo Preflight — Classificador de complexidade de tarefas.

Analisa a descrição de uma tarefa e determina se deve ser
executada diretamente ou delegada via cascade.
"""
from __future__ import annotations

import re
from typing import Literal

# Palavras-chave que indicam execução direta
DIRECT_KEYWORDS: list[str] = [
    "listar", "mostrar", "ver", "status", "ler", "buscar",
    "contar", "qual", "como", "quem", "onde", "quando",
    "ajustar", "mudar", "editar", "corrigir", "typo",
    "remover", "css", "padding", "margin", "cor", "fonte",
]

# Palavras-chave que indicam cascade
CASCADE_KEYWORDS: list[str] = [
    "deploy", "build", "test", "refatorar", "criar",
    "feature", "migrar", "configurar", "implementar",
    "instalar", "publicar", "release",
]

# Palavras-chave que indicam cascade profundo
CASCADE_DEEP_KEYWORDS: list[str] = [
    "deploy", "test", "refatorar",
]

PreflightResult = Literal["direct", "cascade", "cascade-deep"]


def preflight_classify(description: str) -> PreflightResult:
    """
    Classifica a complexidade de uma tarefa.

    Regras:
    - Se contém palavras DIRECT → direct
    - Se contém 2+ CASCADE_DEEP → cascade-deep
    - Se contém palavras CASCADE → cascade
    - Padrão → direct
    """
    desc_lower = description.lower()

    # Direct keywords têm prioridade máxima
    for kw in DIRECT_KEYWORDS:
        if re.search(r'\b' + re.escape(kw) + r'\b', desc_lower):
            return "direct"

    # Cascade deep: 2+ deep keywords
    deep_count = sum(
        1 for kw in CASCADE_DEEP_KEYWORDS
        if re.search(r'\b' + re.escape(kw) + r'\b', desc_lower)
    )
    if deep_count >= 2:
        return "cascade-deep"

    # Cascade: 1+ cascade keywords
    for kw in CASCADE_KEYWORDS:
        if re.search(r'\b' + re.escape(kw) + r'\b', desc_lower):
            return "cascade"

    return "direct"
