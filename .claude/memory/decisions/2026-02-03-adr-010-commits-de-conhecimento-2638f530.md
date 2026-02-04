# ADR-010: Commits de Conhecimento

**ID**: 2638f530
**Autor**: [[@engram]]
**Data**: 2026-02-03
**Labels**: Decision, ADR

---

## Contexto
Precisamos de convenção para commits que modificam .claude/ para facilitar histórico e blame.

## Decisão
Usar prefixo `knowledge(@autor):` para commits de conhecimento:

```
knowledge(@joao): auth bug resolution session
knowledge(@maria): new billing patterns discovered
decision(@team): ADR-008 approved - git-native architecture
pattern(@pedro): add circuit-breaker pattern
episode(@joao): production incident post-mortem
```

## Consequências
- ✅ Fácil filtrar: `git log --grep="knowledge(@joao)"`
- ✅ Blame mostra quem contribuiu conhecimento
- ✅ Consistente com conventional commits
- ⚠️ Requer disciplina da equipe

