# ADR-007: Adoção do Engram (Bootstrap)

**ID**: bcec1e40
**Autor**: [[@engram]]
**Data**: 2026-02-03
**Labels**: Decision, ADR

---

## Contexto
Este projeto É o próprio Engram — um caso metacircular onde o sistema gerencia a si mesmo.

## Decisão
Usar Engram para desenvolver Engram, demonstrando o conceito de auto-alimentação (ouroboros).

## Consequências
- ✅ Dogfooding — usamos o que construímos
- ✅ Bugs encontrados mais rápido
- ✅ Demonstra viabilidade do sistema
- ⚠️ Bootstrap paradox (precisamos do sistema para melhorar o sistema)

