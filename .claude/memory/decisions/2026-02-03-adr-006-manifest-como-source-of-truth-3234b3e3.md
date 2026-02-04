# ADR-006: Manifest como Source of Truth

**ID**: 3234b3e3
**Autor**: [[@engram]]
**Data**: 2026-02-03
**Labels**: Decision, ADR

---

## Contexto
Precisamos saber quais componentes existem, suas versões, uso, saúde.

## Decisão
manifest.json é o registro central. register.py mantém sincronizado. doctor.py detecta dessincronização.

## Consequências
- ✅ Single source of truth
- ✅ Métricas de uso automáticas
- ✅ Health tracking
- ⚠️ Precisa manter sincronizado

