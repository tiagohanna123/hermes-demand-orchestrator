# Changelog — Hermes Demand Orchestrator

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado no [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.0] — 2025-05-05

### Adicionado

- **Journal** — Write-ahead log append-only em formato JSONL
  - Estrutura `JournalEntry` com suporte a ID, timestamp, status, descrição, agente e resumo
  - Leitura, escrita, filtragem e compactação do journal
  - Backup automático antes da compactação
- **Preflight** — Classificador de complexidade de tarefas
  - Três níveis: `direct`, `cascade`, `cascade-deep`
  - Análise por palavras-chave com detecção inteligente
- **Cascade** — Motor de decisão para swarm cascade
  - Classificação complementar ao preflight
  - Suporte a cascata simples e profunda
- **Router** — Roteamento multi-projeto por keywords
  - Detecção automática do projeto alvo baseado na descrição da tarefa
  - Suporte a 8+ projetos (portfolio-dev, sarau-secreto, music-connect, hermes-terminal, etc.)
- **Snapshot** — Gerador de relatórios markdown do estado do journal
  - Agrupamento por status
  - Seções separadas para ativas, completadas e com problemas
- **CLI** — Interface de linha de comando completa (`hermes-orq`)
  - Comandos: `status`, `list`, `preflight`, `route`, `register`, `archive`, `snapshot`, `search`, `filter`, `shell-completion`
  - Suporte a bash e zsh completion
  - Argumento `--journal` para caminho customizado do journal
- **Arquitetura modular** — Separação clara entre journal, preflight, cascade, router e snapshot
- **Testes** — Suíte de testes com pytest para todos os módulos principais
- **Documentação inicial** — Docstrings e anotações de tipo em todo o código

[0.1.0]: https://github.com/hermes-agents/hermes-demand-orchestrator/releases/tag/v0.1.0
