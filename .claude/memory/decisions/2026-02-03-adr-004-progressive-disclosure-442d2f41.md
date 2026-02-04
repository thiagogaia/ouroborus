# ADR-004: Progressive Disclosure

**ID**: 442d2f41
**Autor**: [[@engram]]
**Data**: 2026-02-03
**Labels**: Decision, ADR

---

## Contexto
Carregar todos os skills no início desperdiça tokens e sobrecarrega o contexto.

## Decisão
Skills são carregados sob demanda quando o Claude detecta necessidade (via triggers na description) ou quando invocados explicitamente.

## Consequências
- ✅ Menor uso de tokens
- ✅ Contexto mais focado
- ✅ Escalável para muitos skills
- ⚠️ Descriptions devem ter triggers claros

