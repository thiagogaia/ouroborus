# PAT-004: Estrutura de Command

**ID**: 5509ec9d
**Autor**: [[@engram]]
**Data**: 2026-02-05
**Labels**: Pattern, ApprovedPattern

---

- **Contexto**: ao criar um novo slash command
- **Solução**: seguir schema em `.claude/schemas/command.schema.md`
  - Arquivo único .md em .claude/commands/
  - SEM frontmatter (diferente de skills/agents)
  - Instruções diretas para o Claude
- **Exemplo**: `.claude/commands/commit.md`
- **Descoberto em**: 2026-02-03
