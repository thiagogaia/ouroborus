# ADR-001: Sistema Metacircular

**ID**: 342f8408
**Autor**: [[@engram]]
**Data**: 2026-02-05
**Labels**: Decision, ADR

---

## Contexto
Engram v1 tinha skills fixos. Adicionar novos exigia edição manual. Cada projeto tinha os mesmos skills, mesmo que a stack fosse diferente.

## Decisão
Implementar sistema metacircular onde genesis gera skills sob demanda baseado na stack detectada, e evolution rastreia uso para propor melhorias.

## Consequências
- ✅ Skills customizados por projeto
- ✅ Sistema se auto-evolui
- ✅ Menos manutenção manual
- ⚠️ Maior complexidade inicial
- ⚠️ Requer schemas bem definidos

