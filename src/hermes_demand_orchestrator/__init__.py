"""
Hermes Demand Orchestrator — orquestração de demandas com persistência write-ahead.

Componentes:
- Journal: append-only JSONL write-ahead log
- Preflight: classificador de complexidade (direct vs cascade vs cascade-deep)
- Cascade: lógica de decisão para swarm cascade
- Snapshot: gerador de snapshots legíveis do journal
- Router: roteador multi-projeto por keywords
"""

__version__ = "1.0.0"
