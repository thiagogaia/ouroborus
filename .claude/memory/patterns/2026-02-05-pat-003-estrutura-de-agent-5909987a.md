# PAT-003: Estrutura de Agent

**ID**: 5909987a
**Autor**: [[@engram]]
**Data**: 2026-02-05
**Labels**: Pattern, ApprovedPattern

---

- **Contexto**: ao criar um novo agent
- **Solução**: seguir schema em `.claude/schemas/agent.schema.md`
  - Arquivo único .md em .claude/agents/
  - Frontmatter YAML com name, description, tools
  - Body com responsabilidades, regras, output esperado
- **Exemplo**: `.claude/agents/architect.md`
- **Descoberto em**: 2026-02-03
