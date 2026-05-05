# Arquitetura — Hermes Demand Orchestrator

> Visão estrutural do motor de orquestração de demandas.

---

## Visão Geral (3 camadas)

```
┌──────────────────────────────────────────────────┐
│                    CLI Layer                      │
│            hermes-orq (argparse)                  │
│   status  list  preflight  route  register        │
│   archive  snapshot  search  filter  completion   │
└──────────────────────┬───────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────┐
│                 Engine Layer                       │
│  ┌─────────┐ ┌──────────┐ ┌────────┐ ┌────────┐  │
│  │ Journal  │ │ Preflight│ │Cascade │ │ Router │  │
│  │ (WAL)   │ │(classify)│ │(depth) │ │(proj.) │  │
│  └────┬────┘ └──────────┘ └────────┘ └────────┘  │
│       │         ┌──────────┐                      │
│       │         │ Snapshot │                      │
│       │         │ (report) │                      │
│       │         └──────────┘                      │
└───────┼───────────────────────────────────────────┘
        │
┌───────▼───────────────────────────────────────────┐
│              Storage Layer                         │
│                                                    │
│  ~/.hermes/demanda-journal.jsonl  (append-only)    │
│                                                    │
│  Formato: JSONL — uma entrada JSON por linha       │
│  Garantia: O(1) append, zero parsing na escrita    │
└────────────────────────────────────────────────────┘
```

---

## Fluxo de uma Demanda

```
1. Usuário fala "faz X no sarau"
         │
         ▼
2. Write-Ahead Log (append-only, O(1))
   └─→ ~/.hermes/demanda-journal.jsonl
         │
         ▼
3. Preflight — classifica complexidade
   ├─ direct:     execução direta (listar, mostrar, ler)
   ├─ cascade:    delegar pra subagente (criar, deploy, test)
   └─ cascade-deep: cascata profunda (deploy+test, feature+test+doc)
         │
         ▼
4. Cascade — lógica de decisão complementar
   ├─ direct:     conjunto de palavras-chave
   ├─ cascade:    conjunto de palavras-chave
   └─ deep:       conjunto de palavras-chave
         │
         ▼
5. Router — detecta projeto alvo
   ├─ portfolio-dev, sarau-secreto, music-connect
   ├─ hermes-terminal, hermes-agent-soul
   └─ kanban-orchestrator, mvs-website, intelligence-engine
         │
         ▼
6. Snapshot — geração de relatório markdown
   └─ Agrupamento por status (ativas, completadas, problemas)
```

---

## Módulos

### Journal (`journal.py`)

| Função | Descrição |
|--------|-----------|
| `JournalEntry` | Dataclass: id, ts, status, desc, agent, summary |
| `write_entry()` | Append O(1) — escreve JSON no final do arquivo |
| `read_journal()` | Lê todas as entradas, retorna lista |
| `get_journal_path()` | Resolve path, expande ~ |
| `compact_journal()` | Remove entradas intermediárias, mantém só a última de cada ID |
| `count_entries()` | Contagem total de linhas |

### Preflight (`preflight.py`)

| Função | Descrição |
|--------|-----------|
| `preflight_classify()` | Retorna "direct", "cascade" ou "cascade-deep" |

Classificação por conjuntos de palavras-chave:
- **Direct** (36 palavras): listar, mostrar, ver, status, ler, buscar, contar, qual, como, ajustar, mudar, editar, corrigir, typo, remover, css, padding
- **Cascade** (8 palavras): deploy, build, test, refatorar, criar, feature, migrar, configurar
- **Cascade-deep**: combinações como "deploy" + "test", "refatorar" + "test", "feature" + "test" + "doc"

### Cascade (`cascade.py`)

| Função | Descrição |
|--------|-----------|
| `classify_task()` | Retorna "direct", "cascade" ou "deep" |

Complementa o preflight com conjuntos de palavras (set split):
- **direct_words** (42): listar, mostrar, ver, status, ler, buscar, contar, qual, como, ajustar, mudar, editar, corrigir, typo, remover, css, padding...
- **cascade_words** (15): deploy, build, test, refatorar, criar, feature, migrar, configurar, instalar, iniciar...
- **deep_markers** (8): pipeline, integração, completo, end-to-end, full-stack, migração, refatoração, arquitetura

### Router (`router.py`)

| Função | Descrição |
|--------|-----------|
| `detect_project()` | Retorna slug do projeto ou None |
| `ProjectRule` | Dataclass: nome, keywords, path |

Projetos suportados:
- `portfolio-dev`, `sarau-secreto`, `music-connect`, `hermes-terminal`
- `hermes-agent-soul`, `kanban-orchestrator`, `mvs-website`, `intelligence-engine`

### Snapshot (`snapshot.py`)

| Função | Descrição |
|--------|-----------|
| `generate_snapshot()` | Retorna string markdown com estado atual |
| Agrupamento | Ativas (processing, delegated, failed, blocked) |
| | Completadas |
| | Métricas: total, por status |

---

## CLI (`hermes-orq` — 10 comandos)

```bash
hermes-orq status                    # Estado atual do journal
hermes-orq list --status failed      # Demandas por status
hermes-orq preflight "descrição"     # Classifica tarefa
hermes-orq route "descrição"         # Detecta projeto
hermes-orq register "[--id X] [--agent Y] descrição"  # Registra no journal
hermes-orq archive [--motivo "X"]    # Arquivar emperradas
hermes-orq snapshot -o relatorio.md  # Snapshot markdown
hermes-orq search "texto"            # Busca textual
hermes-orq filter --since 2026-05-01 # Filtro temporal
hermes-orq shell-completion bash     # Autocomplete bash/zsh
```

---

## Armazenamento

### Formato JSONL

Cada linha é um JSON independente:

```json
{"id":"003","ts":"2026-05-03T12:00","status":"registered","desc":"...","agent":"opcional","summary":"opcional"}
```

### Características

- **Append-only**: nova linha no final do arquivo, sempre O(1)
- **Zero corrupção**: não há reescrita ou edição de linhas existentes
- **Estado atual**: última entrada de cada ID (lido com `read-journal.py` ou `tac | python3`)
- **Snapshot**: `demanda-registry.md` é um snapshot legível regenerável

---

## Medições (v0.2.0)

| Métrica | Valor |
|---------|-------|
| Testes | 215 — todos passando (0.29s) |
| Cobertura | 100% (fail_under=90) |
| flake8 | 0 erros (79 chars nas src, 100 nos testes) |
| ruff | All checks passed |
| mypy strict | 0 erros em 7 source files |
| Build | sdist + wheel, 0 deprecation warnings |
| CI | GitHub Actions: test matrix 3.11/3.12/3.13 + lint + typecheck + build |

---

## Diagrama de Dependências

```
hermes-orq (CLI)
├── journal.py       ←── journal.jsonl
├── preflight.py     ←── (regras estáticas)
├── cascade.py       ←── (regras estáticas)
├── router.py        ←── (regras estáticas)
└── snapshot.py      ←── journal.py
```

Nenhum módulo tem dependências externas além de `pyyaml` (para futuras configs YAML) e `stdlib`.
