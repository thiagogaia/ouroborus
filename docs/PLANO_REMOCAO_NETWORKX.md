# Plano: Remoção do networkx do setup

**Objetivo**: Remover networkx da instalação do Brain. O backend principal (`brain_sqlite.py`) não usa networkx; `brain.py` (legado) tem `FallbackGraph` quando networkx não está disponível.

**Impacto**: Nenhum no fluxo normal. Setup mais leve.

---

## Checklist de alterações

### 1. setup.sh

| Linha | Atual | Novo |
|-------|-------|------|
| 422 | `pip install networkx numpy sentence-transformers` | `pip install numpy sentence-transformers` |
| 491 | `... networkx numpy sentence-transformers chromadb ...` | `... numpy sentence-transformers chromadb ...` |
| 503 | `pip install --quiet networkx numpy` + mensagem "networkx + numpy instalados" | `pip install --quiet numpy` + mensagem "numpy instalado" |
| 515 | `... networkx numpy sentence-transformers ...` | `... numpy sentence-transformers ...` |

### 2. docs/QUICKSTART.md

| Linha ~139 | Atual | Novo |
|------------|-------|------|
| Comando manual | `pip install networkx numpy sentence-transformers chromadb pydantic-settings` | `pip install numpy sentence-transformers chromadb pydantic-settings` |

### 3. .claude/brain/README.md

| Linha 28 | Atual | Novo |
|----------|-------|------|
| Instalação | `pip install networkx numpy sentence-transformers chromadb pydantic-settings` | `pip install numpy sentence-transformers chromadb pydantic-settings` |

### 4. Documentação secundária (opcional)

| Arquivo | Ajuste |
|---------|--------|
| `docs/USE_CASES.md` | Remover "networkx" da lista de deps (linha 147) |
| `docs/ANALISE_ENGRAM_COMPLETA.md` | Atualizar "numpy, networkx, sentence-transformers" → "numpy, sentence-transformers" (linha 107) |
| `.claude/knowledge/domain/DOMAIN.md` | Atualizar `install_brain_deps` → "numpy sentence-transformers" (linha 300) |
| `.claude/knowledge/patterns/PATTERNS.md` | Atualizar "(numpy, networkx)" → "(numpy)" (linha 475) |

### 5. Sem alteração

| Arquivo | Motivo |
|---------|--------|
| `.claude/brain/brain.py` | Import opcional + FallbackGraph já existem; comentário pode ser atualizado para "numpy" apenas |
| `tests/brain/conftest.py` | Continua bloqueando networkx para testes — não depende de estar instalado |
| `.claude/knowledge/decisions/ADR_LOG.md` | Histórico; não alterar |

---

## Ordem de execução sugerida

1. **setup.sh** — alterações principais
2. **docs/QUICKSTART.md** — comando de fallback do usuário
3. **.claude/brain/README.md** — instrução de instalação do Brain
4. **brain.py** — comentário linha 37: `(numpy, networkx)` → `(numpy)` apenas (opcional)
5. **Docs secundários** — USE_CASES, ANALISE_ENGRAM_COMPLETA, DOMAIN, PATTERNS

---

## Validação pós-remoção

```bash
# 1. Instalação limpa
rm -rf .claude/brain/.venv
./setup.sh --force .

# 2. Verificar que recall funciona
.claude/brain/.venv/bin/python3 .claude/brain/recall.py "teste" --top 1

# 3. Verificar que sleep funciona
.claude/brain/.venv/bin/python3 .claude/brain/sleep.py 2>/dev/null || true

# 4. Rodar testes do brain
cd tests && python -m pytest brain/ -v -x 2>/dev/null | tail -20
```

---

## Rollback

Se houver problema, reverter os commits ou adicionar networkx de volta na linha 503:
```bash
pip install --quiet networkx numpy 2>/dev/null && print_done "networkx + numpy instalados"
```
