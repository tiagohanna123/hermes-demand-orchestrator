# Estendendo o Hermes Demand Orchestrator

## Adicionando Novas Regras de Projeto (Router)

Edite `src/hermes_demand_orchestrator/router.py` e adicione
um novo `ProjectRule` à lista `PROJECTS`:

```python
ProjectRule("meu-projeto", ["keyword1", "keyword2"], "~/meu-projeto")
```

## Adicionando Novas Keywords (Preflight)

Edite as listas em `src/hermes_demand_orchestrator/preflight.py`:

```python
DIRECT_KEYWORDS.append("minha-keyword-direct")
CASCADE_KEYWORDS.append("minha-keyword-cascade")
```

## Adicionando Novos Projetos (Router)

O Router suporta detecção por keyword. Quanto mais específica
a keyword, maior o score — a melhor correspondência vence.

## Plugins de Pós-Processamento

Para adicionar hooks pós-journal (ex: notificação, webhook),
crie um módulo em `src/hermes_demand_orchestrator/plugins/`:

```python
def on_demand_completed(entry: JournalEntry) -> None:
    """Chamado após uma demanda ser completada."""
    ...
```

E registre no `__main__.py`.

## Integração com Hermes Agent

O Orquestrador lê/ escreve no mesmo `~/.hermes/demanda-journal.jsonl`
que o Hermes Agent. Não há camada extra de integração — o arquivo
é o ponto de contato.

## CI/CD

O projeto usa GitHub Actions com matrix 3.11/3.12/3.13.

Para adicionar um novo Python, edite a matrix no `.github/workflows/test.yml`.
