# Roadmap — Hermes Demand Orchestrator

> Visão de evolução do projeto, da v0.1.0 à v1.0.0.

---

## v0.1.0 — Fundação (Lançada)

**Features:**
- Journal append-only write-ahead log (JSONL)
- Preflight classifier: `direct` / `cascade` / `cascade-deep`
- Cascade decision engine
- Snapshot generator (markdown report)
- Router multi-projeto por keywords
- CLI (`hermes-orq`) com comandos: `status`, `list`, `preflight`, `route`, `register`, `archive`, `snapshot`, `search`, `filter`, `shell-completion`
- Suporte bash/zsh completion
- Compactação do journal (remover entradas intermediárias)
- Arquitetura de agentes modulares

---

## v0.2.0 — Persistência & Resiliência (ETA: Julho 2025)

**Features:**
- Backup automático do journal antes de compactação
- Recuperação automática de journal corrompido
- Journal com rotação de arquivos baseada em tamanho
- Hooks pós-registro (notificações, gatilhos)
- Métricas de desempenho básicas (tempo de classificação, volume de entradas)
- Comando `hermes-orq archive --auto` com políticas configuráveis
- Testes de integração para pipeline completo (registro → preflight → cascade)

---

## v0.3.0 — Integração & Observabilidade (ETA: Outubro 2025)

**Features:**
- Export para formatos externos (JSON, CSV, HTML)
- Integração com Hermes Broker para publicação de eventos
- Dashboard web leve (modo read-only do journal)
- Métricas Prometheus expostas via endpoint HTTP opcional
- Comando `hermes-orq export` com filtros avançados
- Logging estruturado (formato JSON)
- Sistema de alertas por status (failed, blocked, interrupted)

---

## v0.4.0 — Swarm & Delegação (ETA: Janeiro 2026)

**Features:**
- Execução automática de cascade via subagentes reais
- Roteador inteligente com aprendizado de padrões
- Priorização de demandas por urgência/impacto
- Políticas de retry para tarefas com falha
- Limpeza automática de demandas órfãs
- Interoperabilidade com Hermes Agent Soul para tarefas multi-domínio
- Plugin system para provedores de execução (local, Docker, API)

---

## v1.0.0 — Produção (ETA: Abril 2026)

**Features:**
- API RESTful completa para integração externa
- Autenticação e autorização via API key
- Documentação completa (docs.hermes-agents.dev)
- Helm chart para deploy Kubernetes
- CI/CD pipeline completo com GitHub Actions
- Cobertura de testes > 90%
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

*Roadmap sujeito a alterações conforme feedback da comunidade e prioridades do projeto.*
