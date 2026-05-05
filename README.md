# Hermes Demand Orchestrator

<p align="center">
  <strong>Orquestração de demandas com write-ahead log, swarm cascade, preflight classifier e multi-project router</strong>
  <br>
  Registro confiável de tarefas, classificação inteligente de complexidade e roteamento para múltiplos projetos.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.11%20|%203.12%20|%203.13-blue" alt="Python">
  <img src="https://img.shields.io/github/license/tiagohanna123/hermes-demand-orchestrator" alt="License">
</p>

---

## Visão Geral

**Hermes Demand Orchestrator** é um motor de orquestração de demandas para agentes de IA, projetado para registrar, classificar, rotear e acompanhar tarefas de forma confiável e estruturada.

### Componentes

| Módulo | Descrição |
|--------|-----------|
| **Journal** | Write-ahead log append-only em JSONL, garantindo persistência O(1) antes de qualquer processamento |
| **Preflight** | Classificador de complexidade de tarefas (direct, cascade, cascade-deep) baseado em palavras-chave |
| **Cascade** | Lógica de decisão para swarm cascade — determina a profundidade de delegação necessária |
| **Router** | Roteador multi-projeto por palavras-chave, detectando o projeto alvo da demanda |
| **Snapshot** | Gerador de snapshots markdown legíveis com o estado atual de todas as demandas |

### Arquitetura

```
CLI (hermes-orq) → Journal (append-only JSONL)
                 → Preflight (classificador)
                 → Cascade (decisão de profundidade)
                 → Router (detecção de projeto)
                 → Snapshot (relatório markdown)
```

---

## Instalação

```bash
# A partir do repositório
git clone https://github.com/tiagohanna123/hermes-demand-orchestrator.git
cd hermes-demand-orchestrator
pip install -e ".[dev]"
```

---

## Uso

### CLI

```bash
# Registra uma nova demanda
hermes-orq register "Implementar página de login no portfolio"

# Lista todas as demandas com filtros
hermes-orq list
hermes-orq list --status processing,failed
hermes-orq list --last 10

# Mostra estado atual resumido
hermes-orq status

# Classifica a complexidade de uma tarefa
hermes-orq preflight "Fazer deploy do site com testes"
# → Preflight: cascade-deep

# Detecta o projeto mais provável para uma tarefa
hermes-orq route "Corrigir CSS do portfolio"
# → portfolio-dev

# Gera snapshot markdown do journal
hermes-orq snapshot --output relatorio.md

# Busca por texto no journal
hermes-orq search "deploy"

# Arquiva demandas emperradas (processing, delegated, interrupted, failed)
hermes-orq archive --motivo "tarefa abandonada"

# Filtra por timestamp e status
hermes-orq filter --since 2025-01-01T00:00:00 --status completed

# Gera script de shell completion
hermes-orq shell-completion bash >> ~/.bashrc
hermes-orq shell-completion zsh >> ~/.zshrc
```

### API Python

```python
from hermes_demand_orchestrator.journal import JournalEntry, write_entry, read_journal
from hermes_demand_orchestrator.preflight import preflight_classify
from hermes_demand_orchestrator.cascade import classify_task
from hermes_demand_orchestrator.router import detect_project
from hermes_demand_orchestrator.snapshot import generate_snapshot
from datetime import datetime, timezone

# Criar e registrar uma demanda
entry = JournalEntry(
    id="task-001",
    ts=datetime.now(timezone.utc),
    status="registered",
    desc="Criar endpoint de login no portfolio",
    agent="hermes-agent",
)
write_entry("~/.hermes/demanda-journal.jsonl", entry)

# Classificar complexidade
result = preflight_classify("Fazer deploy com testes")
print(result)  # "cascade-deep"

# Detectar projeto
project = detect_project("Corrigir CSS do portfolio")
print(project)  # "portfolio-dev"

# Gerar snapshot
snapshot = generate_snapshot("~/.hermes/demanda-journal.jsonl")
print(snapshot)
```

---

## Desenvolvimento

```bash
# Setup
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# Testes
make test           # pytest — verboso
make test-cov       # pytest + coverage
make lint           # flake8
make lint-ruff      # ruff check
make typecheck      # mypy strict
make lint-all       # flake8 + ruff + mypy
make build          # sdist + wheel
make clean          # remove artefatos de build e cache
```

### CI/CD

GitHub Actions executa em cada push:

- Testes (pytest) com matrix Python 3.11/3.12/3.13
- Linting (ruff + flake8)
- Type checking (mypy strict)
- Build (sdist + wheel)

---

## Roadmap

- [x] Journal append-only em JSONL com suporte a compactação
- [x] Preflight classifier (direct / cascade / cascade-deep)
- [x] Cascade decision logic para swarm
- [x] Router multi-projeto por keywords
- [x] Snapshot markdown do estado do journal
- [x] CLI completa (register, list, status, preflight, route, archive, snapshot, search, filter, shell-completion)
- [x] Integração contínua com GitHub Actions
- [ ] Web dashboard para visualização de demandas
- [ ] Notificações via webhook (Slack, Discord)
- [ ] Integração com provedores externos de IA (OpenAI, Claude)
- [ ] Suporte a templates de demanda reutilizáveis

---

## Licença

MIT © Tiago Hanna
