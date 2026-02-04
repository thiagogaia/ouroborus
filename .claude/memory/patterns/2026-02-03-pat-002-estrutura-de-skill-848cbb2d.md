# PAT-002: Estrutura de Skill

**ID**: 848cbb2d
**Autor**: [[@engram]]
**Data**: 2026-02-03
**Labels**: Pattern, ApprovedPattern

---

- **Contexto**: ao criar um novo skill
- **Solução**: seguir schema em `.claude/schemas/skill.schema.md`
  - Diretório kebab-case com SKILL.md obrigatório
  - Frontmatter YAML com name + description (50-500 chars)
  - Scripts em scripts/ com shebang e permissão executável
  - References em references/ para docs sob demanda
- **Exemplo**: `.claude/skills/engram-genesis/`
- **Descoberto em**: 2026-02-03
