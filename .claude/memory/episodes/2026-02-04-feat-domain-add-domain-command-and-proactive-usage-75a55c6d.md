# feat(domain): add /domain command and proactive usage instructions

**ID**: 75a55c6d
**Autor**: [[@thigato]]
**Data**: 2026-02-04
**Labels**: Episode, Feature, DomainDomain

---

Sessão de análise e implementação do sistema de domínio:

1. PROBLEMA IDENTIFICADO: Sistema de domínio existia (domain-expert skill, domain-analyst agent, DOMAIN.md) mas faltava instrução proativa de QUANDO usar automaticamente.

2. SOLUÇÃO IMPLEMENTADA:
   - Criado /domain command em .claude/commands/domain.md
   - Adicionada seção "Quando Usar Domain-Expert Automaticamente" no CLAUDE.md
   - 6 triggers definidos: termo desconhecido, regra implícita, estados de negócio, comentário "por quê", pergunta de negócio, lógica condicional complexa
   - Workflow de descoberta automática: Detectar → Verificar → Extrair → Reportar → Validar

3. PADRÃO APLICADO: Mesmo modelo do /recall (triggers claros + workflow estruturado)

4. ARQUIVOS AFETADOS:
   - CLAUDE.md (+21 linhas)
   - .claude/commands/domain.md (novo, 71 linhas)
   - .claude/manifest.json (registro do command)
