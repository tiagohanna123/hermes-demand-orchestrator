# Roadmap — Hermes Demand Orchestrator

> Visão de evolução do projeto, da v0.1.0 à v1.0.0.

---

## ✓ v0.1.0 — Fundação (Lançada)

**Features:**
- Journal append-only write-ahead log (JSONL)
- Preflight classifier: `direct` / `cascade` / `cascade-deep`
- Cascade decision engine
- Snapshot generator (markdown report)
- Router multi-projeto por keywords
- CLI (`hermes-orq`) com 10 comandos
- Suporte bash/zsh completion
- Compactação do journal

---

## ✓ v0.2.0 — Projeto Formal (Lançada)

**Features:**
- GitHub Actions CI/CD (test matrix 3.11/3.12/3.13 + lint + typecheck + build)
- Release workflow (PyPI trusted publishing + GitHub Release)
- docs/ARCHITECTURE.md com diagrama 3 camadas
- Issue/PR templates
- 215 testes, 100% coverage, flake8 0, ruff 0, mypy strict 0

---

## v0.3.0 — API & Observabilidade (ETA: Julho 2026)

**Features:**
- REST API (FastAPI) via dependência opcional `[api]`
- SSE Event Bus para notificações em tempo real
- Export JSON/CSV
- Dashboard web leve (modo read-only do journal)
- Métricas de desempenho (tempo de classificação, volume de entradas)
- Logging estruturado (formato JSON)
- Sistema de alertas por status (failed, blocked, interrupted)

---

## v0.4.0 — Swarm & Delegação (ETA: Setembro 2026)

**Features:**
- Execução automática de cascade via subagentes reais
- Roteador inteligente com aprendizado de padrões
- Priorização de demandas por urgência/impacto
- Políticas de retry para tarefas com falha
- Limpeza automática de demandas órfãs
- Hooks pós-registro (notificações, gatilhos)
- Plugin system para provedores de execução (local, Docker, API)

---

## v1.0.0 — Produção (ETA: Novembro 2026)

**Features:**
- Documentação completa (docs.hermes-agents.dev)
- Helm chart para deploy Kubernetes
- Benchmarking e relatórios de performance
- Modo cluster com Journal distribuído (etcd / NATS)
- Suporte a plugins de terceiros via PyPI
- Auditoria completa de operações
- SLA monitoring e health check endpoints

---

## Legendas

| Marco | Status |
|-------|--------|
| ✅ | Lançado |
| 🔜 | Em desenvolvimento |
| 📋 | Planejado |

---

*Roadmap sujeito a alterações conforme feedback e prioridades do projeto.*
