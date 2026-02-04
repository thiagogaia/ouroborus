# Fix: Seeds não instalados em .claude/skills/

**ID**: b9a5cadd
**Autor**: [[Thiago Gaia]]
**Data**: 2026-02-03
**Labels**: Episode, BugFix

---

Seeds existiam em core/seeds/ mas não eram copiados para .claude/skills/. Corrigido copiando todos os 6 seeds universais: project-analyzer, knowledge-manager, domain-expert, priority-engine, code-reviewer, engram-factory.
