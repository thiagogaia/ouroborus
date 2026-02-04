# PAT-009: Versionamento de Componentes

**ID**: c3ac2a3a
**Autor**: [[@engram]]
**Data**: 2026-02-03
**Labels**: Pattern, ApprovedPattern

---

- **Contexto**: ao evoluir um componente existente
- **Solução**:
  - archive.py faz backup em .claude/versions/
  - Incrementar versão no manifest
  - Registrar mudança no evolution-log.md
- **Descoberto em**: 2026-02-03
