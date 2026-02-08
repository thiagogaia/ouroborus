---
name: knowledge-manager
description: Motor de retroalimentação do Engram. Gerencia o ciclo de registro
  de conhecimento nos arquivos persistentes. Use ao final de tarefas, durante
  /learn, ou quando precisar registrar padrões, decisões, estado ou domínio.
  Coração do sistema — sem ele o ciclo não fecha.
---

# Knowledge Manager

Gerencia o ciclo de retroalimentação — o coração do Engram.

**Todo conhecimento novo** (decisões, padrões, experiências, conceitos) vai via `brain.add_memory()`. O cérebro é a única entrada. O recall é a forma de consultar.

## Onde Registrar

| Tipo | Como |
|------|------|
| Decisão, Padrão, Experiência, Conceito, Estado | `brain.add_memory()` — cérebro é a única entrada |
| Prioridades (tarefas, ICE Score) | `PRIORITY_MATRIX.md` — único .md editável |

## Workflow de Registro

### 1. Identificar Tipo de Conhecimento
Classifique o que foi aprendido/decidido/feito:
- **Estado** → cérebro via `brain.add_memory()` (labels: ["State"])
- **Padrão** → cérebro via `brain.add_memory(labels=["Pattern", "ApprovedPattern"])`
- **Decisão** → cérebro via `brain.add_memory(labels=["Decision", "ADR"])`
- **Prioridade** → PRIORITY_MATRIX.md (incluir: ICE Score) — único .md ativo
- **Domínio** → cérebro via `brain.add_memory(labels=["Concept", "Glossary"])`
- **Experiência** → cérebro via `brain.add_memory(labels=["Episode", "Experience"])`

### 2. Registrar no Lugar Correto
- **Cérebro**: `brain.add_memory()` — evitar duplicação conferindo via recall antes
- **PRIORITY_MATRIX.md**: tarefas, ICE Score (ver schema em `.claude/dna/knowledge.schema.md`)

### 3. Cross-Reference
Se o registro impacta outros files, atualize-os também:
- ADR que cria padrão → registrar ambos no cérebro com `references=`
- Padrão que resolve prioridade → atualizar PRIORITY_MATRIX.md
- Estado que revela bloqueio → atualizar PRIORITY_MATRIX.md

### 4. Limpar Obsoletos
- Mover tarefas completas para "Cemitério" no PRIORITY_MATRIX.md
- Padrões/ADRs depreciados: registrar no cérebro com `props={"status": "Depreciado"}` ou novo nó que referencia o antigo

## ICE Score (para PRIORITY_MATRIX)

```
ICE = (Impacto × Confiança) / Esforço
```

- **Impacto** (1-10): quanto valor entrega se concluído
- **Confiança** (1-10): quão certo estamos de que funciona
- **Esforço** (1-10): quanto trabalho exige (1=pouco, 10=muito)

Exemplo: Feature com alto impacto (8), boa confiança (7), esforço médio (5) = (8×7)/5 = 11.2

## Regras
- NUNCA delete conhecimento — marque como obsoleto
- SEMPRE inclua data em cada entrada
- SEMPRE mantenha o formato do schema
- Se em dúvida sobre onde registrar: registre no cérebro via `brain.add_memory()`
- Desprioritização é tão importante quanto priorização
- Máximo 50 entradas em EXPERIENCE_LIBRARY.md (manter as mais úteis)
