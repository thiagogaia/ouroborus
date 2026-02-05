# PAT-007: Validação Antes de Registro

**ID**: 7ba9e33c
**Autor**: [[@engram]]
**Data**: 2026-02-05
**Labels**: Pattern, ApprovedPattern

---

- **Contexto**: antes de registrar componente
- **Solução**: rodar validate.py primeiro
  - `python3 validate.py --type skill --path .claude/skills/nome/`
  - Corrigir todos os erros antes de registrar
- **Descoberto em**: 2026-02-03
