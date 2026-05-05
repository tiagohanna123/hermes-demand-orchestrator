# Contribuindo para o Hermes Demand Orchestrator

Obrigado pelo interesse em contribuir! 🙌

## Stack

- Python >= 3.11
- pytest + pytest-asyncio + pytest-cov + pytest-timeout
- pyyaml (configuração YAML)
- ruff + flake8 + mypy (lint/type check)
- black + isort (formatação)
- pre-commit (hooks automatizados)
- build (empacotamento)
- uv (recomendado) ou pip para gerenciamento de pacotes

## Setup do ambiente

```bash
# Clone o repositório
git clone https://github.com/tiagohanna/hermes-demand-orchestrator.git
cd hermes-demand-orchestrator

# Crie e ative o virtualenv (recomendado: uv)
uv venv
source .venv/bin/activate

# Instale o projeto em modo editável com dependências de dev
uv pip install -e ".[dev]"
```

## Desenvolvimento

### Comandos principais

| Comando | Descrição |
| ------- | --------- |
| `make test` | Executa testes com pytest (modo verboso) |
| `make test-cov` | Executa testes com relatório de cobertura (HTML + terminal) |
| `make lint` | Lint com flake8 (src/ tests/) |
| `make lint-ruff` | Lint com ruff (src/ tests/) |
| `make lint-ruff-fix` | Corrige automaticamente o que ruff puder |
| `make typecheck` | Type check com mypy strict (src/) |
| `make lint-all` | flake8 + ruff + mypy |
| `make clean` | Remove artefatos de build e cache |
| `make build` | Constrói pacote (sdist + wheel) |
| `make precommit` | Executa pre-commit em todos os arquivos |
| `make all` | Instala, lint completo, testa com cobertura e build |

### Lint

```bash
# flake8 — estilo e erros comuns
make lint

# ruff — linting moderno e rápido
make lint-ruff

# mypy — checagem de tipos estática
make typecheck

# Tudo de uma vez
make lint-all
```

### Testes

```bash
# Todos os testes
make test

# Com cobertura
make test-cov

# Relatório HTML da cobertura
make test-cov
open htmlcov/index.html

# Apenas um arquivo
python -m pytest tests/test_journal.py -v

# Apenas um teste específico
python -m pytest tests/test_journal.py::test_write_and_read -v

# Com print e debug
python -m pytest tests/ -v -s
```

### Cobertura

A cobertura mínima exigida é de **90%** (`fail_under = 90` no `pyproject.toml`).

```bash
make test-cov
# Relatório HTML: open htmlcov/index.html
```

## Estrutura do projeto

```
src/hermes_demand_orchestrator/
├── __init__.py          # API pública e docstring do pacote
├── __main__.py          # CLI entry point (argparse, 10 subcomandos)
├── journal.py           # JournalEntry, write-ahead log JSONL, compactação
├── preflight.py         # Preflight classifier (direct/cascade/cascade-deep)
├── cascade.py           # Cascade decision logic
├── router.py            # Multi-project router por keywords
└── snapshot.py          # Gerador de snapshot markdown
tests/
├── __init__.py
├── conftest.py          # Fixtures compartilhadas
├── test_journal.py      # Testes do write-ahead log
├── test_preflight.py    # Testes do classificador preflight
├── test_cascade.py      # Testes da lógica cascade
├── test_router.py       # Testes do roteador
└── test_snapshot.py     # Testes do gerador de snapshot
```

## Padrões de código

### Novos módulos

Para adicionar um novo módulo (ex: um novo classificador ou integração):

1. Crie `src/hermes_demand_orchestrator/novo_modulo.py`
2. Siga o padrão de docstring e tipagem dos módulos existentes
3. Adicione testes correspondentes em `tests/test_novo_modulo.py`
4. Exponha a API pública em `__init__.py` se aplicável

### Novos projetos no Router

Para adicionar um novo projeto ao roteador em `router.py`:

```python
ProjectRule("meu-projeto", ["keyword1", "keyword2"], "~/caminho/do/projeto"),
```

Adicione a entrada na lista `PROJECTS` com:
- Nome do projeto (slug)
- Lista de palavras-chave para detecção
- Caminho opcional para o diretório do projeto

### Novas keywords no Preflight/Cascade

Para ajustar a classificação de complexidade:

```python
# Em preflight.py
DIRECT_KEYWORDS.append("keyword")
CASCADE_KEYWORDS.append("keyword")
CASCADE_DEEP_KEYWORDS.append("keyword")

# Em cascade.py — mesma lógica
DIRECT_WORDS.add("keyword")
CASCADE_WORDS.add("keyword")
DEEP_WORDS.add("keyword")
```

### Commits

Usamos commits semânticos:

- `feat:` — nova funcionalidade
- `fix:` — correção de bug
- `docs:` — documentação
- `refactor:` — refatoração
- `test:` — testes
- `style:` — formatação de código
- `ci:` — CI/CD
- `chore:` — manutenção
- `perf:` — melhoria de performance

### Pull Requests

1. Crie um branch a partir de `main`
2. Faça suas alterações seguindo os padrões de código
3. Garanta que `make lint-all && make test-cov` passe
4. Abra o PR com descrição clara do que mudou e por quê
5. Inclua screenshots ou exemplos de uso quando relevante

## Dúvidas

Abra uma issue em https://github.com/tiagohanna/hermes-demand-orchestrator/issues
