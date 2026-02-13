# Plano: Recall retornar conteúdo completo (remover truncamento de 2000 chars)

---

## Contexto

O recall limita o `content` na resposta para **2000 caracteres**, enquanto:
- **Ingest**: não trunca
- **Brain storage**: não trunca
- **Recall output**: trunca em 2000 chars ← o gargalo

O `brain_sqlite` já tem `expand_nodes()`, que devolve o conteúdo completo sem truncar (linhas 1468–1469). Para um fluxo só no cérebro, hoje seria preciso:
1. Usar o recall para achar os IDs
2. Chamar `expand_nodes` com esses IDs para pegar o conteúdo inteiro

**Objetivo**: Remover o limite no recall para retornar o conteúdo inteiro em uma única chamada (fluxo brain-only sem round-trip extra).

---

## Análise do codebase

| Arquivo       | Local   | Trunca? | Limite    |
|---------------|---------|---------|-----------|
| `recall.py`   | L211    | Sim     | 2000 chars (content no JSON) |
| `recall.py`   | L309    | Sim     | 200 chars (formato human, full mode) |
| `recall.py`   | L342    | Sim     | 500 chars (formato human, expand mode) |
| `brain_sqlite.py` | L1468 | Não | `expand_nodes()` usa `props.get("content", "")` inteiro |

---

## Plano de implementação

```
📋 Plano: Recall retornar content completo
══════════════════════════════════════════
Complexidade: baixa
Estimativa: 3 steps, ~15 min
Impacta: .claude/brain/recall.py

Steps:
  1. Remover truncamento em search_brain (L211)
     - De: "content": node_content[:2000] if node_content else None
     - Para: "content": node_content if node_content else None

  2. (Opcional) Ajustar formatação human-readable para não quebrar output muito longo
     - L309: manter [:200] ou aumentar? → Decisão: manter preview curto para human;
       o JSON é o contrato principal (consumido por comandos, CLAUDE.md)
     - L342: expand já usa expand_nodes → content vem completo; truncar em 500
       é só para exibição no terminal

  3. Validar: recall JSON passa a ter content completo; formatação human
     continua legível (preview)
```

---

## Decisões

### 1. JSON vs human-readable

- **JSON** (`--format json`): deve retornar `content` completo — é usado por comandos e fluxo automático (CLAUDE.md).
- **Human-readable**: pode manter preview curto (200/500 chars) para evitar flood de texto no terminal; o usuário pode usar `--format json` se quiser o conteúdo inteiro.

### 2. Riscos e mitigação

| Risco              | Mitigação |
|--------------------|-----------|
| Payload JSON muito grande | `--top` já limita nº de resultados; memórias enormes (>50KB cada) são raras |
| Token limit em prompts  | Quem consome (ex: /plan, /recall) usa `--top`; fluxo brain-only continua controlado por `top_k` |

---

## Implementação mínima (suficiente)

Alteração em **um único ponto**:

```python
# recall.py, linha 211
"content": node_content if node_content else None,  # sem [:2000]
```

---

## Verificação

- [ ] Recall com `--format json` retorna `content` completo nos resultados
- [ ] Recall human-readable continua exibindo preview legível (sem mudar L309/L342)
- [ ] Fluxo brain-only (CLAUDE.md) passa a ter conteúdo integral sem `--expand`
