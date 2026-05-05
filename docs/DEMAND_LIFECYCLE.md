# Ciclo de Vida de uma Demanda

## Estados

```
                  ┌──────────┐
                  │ REGISTERED│
                  └────┬─────┘
                       │
                  ┌────▼─────┐
                  │PROCESSING│
                  └────┬─────┘
                       │
              ┌────────┼────────┐
              │        │        │
        ┌─────▼──┐ ┌──▼───┐ ┌──▼────┐
        │DELEGATED│ │ CASCADE│ │DIRECT │
        └─────┬──┘ └──────┘ └────┬───┘
              │                  │
        ┌─────▼──┐        ┌─────▼───┐
        │COMPLETED│       │ COMPLETED│
        └─────────┘       └─────────┘
              │                  │
              └────────┬─────────┘
                       │
              ┌────────▼────────┐
              │                 │
        ┌─────▼────┐     ┌─────▼────┐
        │ ARCHIVED  │    │  FAILED   │
        └───────────┘    └──────────┘
                                │
                          ┌─────▼────┐
                          │INTERRUPTED│
                          └──────────┘
                                │
                          ┌─────▼────┐
                          │  BLOCKED │
                          └──────────┘
```

## Transições Válidas

| De | Para | Quando |
|----|------|--------|
| `registered` | `processing` | Início do processamento |
| `processing` | `delegated` | Tarefa delegada a subagente |
| `processing` | `completed` | Execução direta concluída |
| `delegated` | `completed` | Subagente reportou conclusão |
| `processing` | `failed` | Erro durante execução |
| `delegated` | `failed` | Subagente falhou |
| `processing` | `interrupted` | Gateway reiniciou / timeout |
| `delegated` | `interrupted` | Subagente interrompido |
| `failed` | `blocked` | Falha recorrente, requer ação manual |
| `interrupted` | `registered` | Retry automático |
| `failed` | `archived` | Arquivada (cleanup) |
| `interrupted` | `archived` | Arquivada (cleanup) |
| `blocked` | `archived` | Arquivada (cleanup) |
| `completed` | `archived` | Arquivada (cleanup) |
| qualquer | `archived` | Forçado pelo usuário |

## Duração Máxima

| Ambos | Limite |
|-------|--------|
| `processing` sem update | 10 min (timeout watchdog) |
| `delegated` sem retorno | 10 min (timeout subagente) |
| Cascade total | 600s (configurável) |

## Ações Automáticas

| Condição | Ação |
|----------|------|
| `processing` > 10 min | Marcar `interrupted`, retry |
| `failed` 2+ vezes consecutivas | Marcar `blocked` |
| `blocked` > 24h | Sugerir `archived` |
