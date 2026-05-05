# Arquitetura do Hermes Demand Orchestrator

## Visão Geral em 3 Camadas

```
┌──────────────────────────────────────────────────────────────┐
│                         CLI (hermes-orq)                      │
│    status · list · preflight · route · register · archive     │
│    snapshot · search · filter · shell-completion             │
├──────────────────────────────────────────────────────────────┤
│                     Engine de Orquestração                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐ │
│  │ Journal  │  │ Preflight│  │ Cascade  │  │   Router     │ │
│  │ (WAL)    │  │Classifier│  │ Decision │  │Multi-Project │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────┘ │
│  ┌──────────┐                                                │
│  │ Snapshot │                                                │
│  │ Generator│                                                │
│  └──────────┘                                                │
├──────────────────────────────────────────────────────────────┤
│                    Camada de Persistência                     │
│  ┌─────────────────────────────────────────────────────┐     │
│  │        demanda-journal.jsonl (append-only JSONL)     │     │
│  │        ~/.hermes/demanda-journal.jsonl               │     │
│  └─────────────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────────────┘
```

## Componentes

### 1. Journal (Write-Ahead Log)

**Arquivo:** `src/hermes_demand_orchestrator/journal.py`

O coração do sistema. Um append-only JSONL que registra toda demanda ANTES de qualquer processamento.

| Operação | Custo | Descrição |
|----------|-------|-----------|
| `write_entry()` | O(1) | Append de linha JSON |
| `read_journal()` | O(n) | Leitura completa |
| `get_latest_per_id()` | O(n) | Último estado de cada ID |
| `filter_entries()` | O(n) | Filtro por status/agente/data |
| `compact_journal()` | O(n) | Remove entradas intermediárias |

### 2. Preflight Classifier

**Arquivo:** `src/hermes_demand_orchestrator/preflight.py`

Classifica a complexidade de uma tarefa usando regex com boundaries.

| Resultado | Gatilho |
|-----------|---------|
| `direct` | Contém keyword DIRECT (listar, ver, ajustar...) |
| `cascade` | Contém keyword CASCADE (deploy, criar, build...) |
| `cascade-deep` | 2+ deep keywords (deploy + test) |

### 3. Cascade Decision

**Arquivo:** `src/hermes_demand_orchestrator/cascade.py`

Versão simplificada usando `set(str.lower().split())`. Mesma lógica
do Preflight mas sem regex — mais rápida para uso em tempo real.

### 4. Router

**Arquivo:** `src/hermes_demand_orchestrator/router.py`

Detecta a qual projeto uma demanda pertence baseado em keywords
na descrição. Suporta 8+ projetos.

### 5. Snapshot Generator

**Arquivo:** `src/hermes_demand_orchestrator/snapshot.py`

Gera um snapshot markdown legível do estado atual do journal,
agrupado por seções: ativas, completadas, com problemas.

## Fluxo de Dados

```
Demanda chega
  → write_entry(id, "registered")  [WAL]
  → preflight_classify(task)        [direct/cascade/cascade-deep]
  → detect_project(task)            [portfolio/sarau/hermes...]
  → write_entry(id, "processing")
  → Execução (direta ou cascade)
  → write_entry(id, "completed"/"failed")
  → generate_snapshot() (opcional)
```

## Journal: Formato de Dados

```jsonl
{"id":"001","ts":"2026-05-05T12:00:00+00:00","status":"registered","desc":"Fazer deploy"}
{"id":"001","ts":"2026-05-05T12:00:30+00:00","status":"processing"}
{"id":"001","ts":"2026-05-05T12:05:00+00:00","status":"completed","summary":"Build OK"}
```

Cada linha é auto-contida. O estado atual é a última linha de cada ID.
