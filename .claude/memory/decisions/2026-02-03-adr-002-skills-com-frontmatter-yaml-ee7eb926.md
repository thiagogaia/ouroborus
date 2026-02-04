# ADR-002: Skills com Frontmatter YAML

**ID**: ee7eb926
**Autor**: [[@engram]]
**Data**: 2026-02-03
**Labels**: Decision, ADR

---

## Contexto
Precisamos de metadados estruturados (name, description) para validação e registro, mas queremos manter markdown legível.

## Decisão
Usar frontmatter YAML (delimitado por ---) no início de SKILL.md. Body continua markdown puro.

## Consequências
- ✅ Validação automática via parse simples
- ✅ Legível por humanos
- ✅ Compatível com editores markdown
- ⚠️ Parser YAML básico (sem recursos avançados)

