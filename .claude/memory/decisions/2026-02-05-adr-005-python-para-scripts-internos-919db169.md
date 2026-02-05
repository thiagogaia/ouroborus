# ADR-005: Python para Scripts Internos

**ID**: 919db169
**Autor**: [[@engram]]
**Data**: 2026-02-05
**Labels**: Decision, ADR

---

## Contexto
Scripts de genesis/evolution precisam manipular JSON, parsear markdown, validar estruturas.

## Decisão
Usar Python 3 sem dependências externas. Funciona em qualquer máquina com Python instalado.

## Consequências
- ✅ Zero dependências
- ✅ Funciona em macOS, Linux, WSL
- ✅ Fácil de manter
- ⚠️ Requer Python 3.8+

