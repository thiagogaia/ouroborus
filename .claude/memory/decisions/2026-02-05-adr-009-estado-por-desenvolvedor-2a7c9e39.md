# ADR-009: Estado Por Desenvolvedor

**ID**: 2a7c9e39
**Autor**: [[@engram]]
**Data**: 2026-02-05
**Labels**: Decision, ADR

---

## Contexto
Com múltiplos devs trabalhando no mesmo projeto, o arquivo de estado (CURRENT_STATE.md) conflitaria constantemente.

## Decisão
Cada dev tem seu próprio arquivo de estado:

```
.claude/active/state/
├── joao.md       ← contexto do @joao
├── maria.md      ← contexto da @maria
└── _team.md      ← GERADO (merge de todos)
```

- Dev edita só seu arquivo → nunca conflita
- `_team.md` é gerado por script → nunca editado manualmente
- Script roda no /status ou /learn

## Consequências
- ✅ Zero conflitos de merge em estado
- ✅ Cada dev tem contexto personalizado
- ✅ _team.md dá visão geral da equipe
- ⚠️ Precisa identificar dev (identity.json ou git config)

