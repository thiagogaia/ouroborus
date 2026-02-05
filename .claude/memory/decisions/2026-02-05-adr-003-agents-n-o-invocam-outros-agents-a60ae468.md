# ADR-003: Agents Não Invocam Outros Agents

**ID**: a60ae468
**Autor**: [[@engram]]
**Data**: 2026-02-05
**Labels**: Decision, ADR

---

## Contexto
Task tool permite invocar subagents. Se agents pudessem invocar outros agents, poderíamos ter loops infinitos ou explosão de contexto.

## Decisão
Agents são terminais — podem usar tools (Read, Grep, etc) mas NUNCA Task. Orquestração fica com o Claude principal.

## Consequências
- ✅ Sem risco de loops infinitos
- ✅ Controle de contexto previsível
- ✅ Debug mais simples
- ⚠️ Composição requer skill intermediário

