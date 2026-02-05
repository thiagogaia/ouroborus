# PAT-011: Migração Inteligente de Backups

**ID**: 57eaf73d
**Autor**: [[@engram]]
**Data**: 2026-02-05
**Labels**: Pattern, ApprovedPattern

---

- **Contexto**: ao reinstalar Engram em projeto com instalação anterior
- **Solução**: migrate_backup.py com estratégia smart
  - Fase 0 do /init-engram: detectar → analisar → apresentar → migrar
  - Preservar skills/commands/agents customizados (não-core)
  - Merge de permissões no settings.json
  - Merge semântico de knowledge files (append entries únicos)
  - Cleanup na Fase 6 após sucesso
- **Descoberto em**: 2026-02-03
