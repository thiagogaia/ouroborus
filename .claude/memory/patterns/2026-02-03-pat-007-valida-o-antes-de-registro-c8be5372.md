# PAT-007: Validação Antes de Registro

**ID**: c8be5372
**Autor**: [[@engram]]
**Data**: 2026-02-03
**Labels**: Pattern, ApprovedPattern

---

- **Contexto**: antes de registrar componente
- **Solução**: rodar validate.py primeiro
  - `python3 validate.py --type skill --path .claude/skills/nome/`
  - Corrigir todos os erros antes de registrar
- **Descoberto em**: 2026-02-03
