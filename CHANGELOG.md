# Changelog — Hermes Demand Orchestrator

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado no [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] — 2026-05-05

### Adicionado

- **Declaração de Production Readiness** — Projeto promovido a v1.0.0 estável
- **216 testes** — 100% de cobertura em todos os módulos (src/ + tests/)
- **Todos os quality gates** — flake8 0, ruff 0, mypy strict 0, cobertura 90%+

### Melhorado

- **Estabilidade** — Sem alterações de breaking change desde v0.2.1; base sólida para produção
- **Documentação** — CHANGELOG e ROADMAP oficializados para rastreabilidade de versões
- **Governança** — Política de versionamento semântico totalmente estabelecida

---

## [0.2.1] — 2026-05-05

### Adicionado

- **Mypy strict nos testes** — cobertura de type checking expandida para o diretório `tests/` com override para `disallow_untyped_defs`
- **216 testes** — +1 teste para normalização de timestamp naive

### Corrigido

- **40 erros de ruff** — UP017 (timezone.utc → UTC), E501 (linhas longas), S108 (tmp_path), I001 (import sorting), F401 (unused import), B018 (useless expression)
- **Cobertura 100%** — linha 55 do journal.py (naive timestamp normalization) agora testada
- **Mypy lint** — `# type: ignore[arg-type]` obsoleto removido do test_journal.py

### Melhorado

- **Ruff limpo**: 0 erros, 0 warnings
- **Mypy src/ strict**: 0 erros (7 arquivos)
- **Mypy tests/**: 0 erros (7 arquivos)
- **Cobertura**: 100% (208/208 statements)
- **Build**: sdist + wheel sem warnings

---

## [0.2.0] — 2026-05-05

### Adicionado

- **CI/CD** — GitHub Actions workflows completos
  - Workflow `test.yml`: matrix Python 3.11/3.12/3.13 com lint + typecheck + coverage + build
  - Workflow `release.yml`: PyPI (trusted publishing) + GitHub Release com changelog
- **Issue/PR templates** — Bug report, feature request, pull request
- **docs/ARCHITECTURE.md** — Documentação completa da arquitetura (3 camadas, fluxo, módulos, CLI)
- **215 testes** — 100% coverage, flake8 0, ruff 0, mypy strict 0

### Melhorado

- Número de testes saltou de 175 para 215 (+23%)
- Cobertura subiu de 96% para 100%
- Build CI verifica que o pacote instala corretamente via pip

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

[1.0.0]: https://github.com/hermes-agents/hermes-demand-orchestrator/releases/tag/v1.0.0
[0.2.1]: https://github.com/hermes-agents/hermes-demand-orchestrator/releases/tag/v0.2.1
[0.2.0]: https://github.com/hermes-agents/hermes-demand-orchestrator/releases/tag/v0.2.0
[0.1.0]: https://github.com/hermes-agents/hermes-demand-orchestrator/releases/tag/v0.1.0
