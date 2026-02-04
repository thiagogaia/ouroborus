# ADR-008: Arquitetura Git-Native com Grafo de Conhecimento

**ID**: e57d240c
**Autor**: [[@engram]]
**Data**: 2026-02-03
**Labels**: Decision, ADR

---

## Contexto
O Engram precisa escalar para:
- 10+ desenvolvedores por projeto
- 3-5 anos de uso contínuo
- ~25.000 episódios, ~125.000 eventos ao longo do tempo
- Múltiplas organizações usando o sistema

Problemas a resolver:
1. **Sync entre devs**: Como compartilhar conhecimento sem conflitos?
2. **Custo de tokens**: Claude não pode ler 25k arquivos (12.5M tokens = $37/sessão)
3. **Assertividade**: Como encontrar conhecimento relevante em massa de dados?
4. **Simplicidade**: Evitar infraestrutura cloud complexa

## Decisão
Adotar arquitetura **Git-native com grafo de conhecimento estilo Obsidian**:

## Consequências
**Benefícios:**
- ✅ Zero custo de infraestrutura (Git já existe)
- ✅ Funciona 100% offline
- ✅ Histórico completo grátis (git log)
- ✅ Review de conhecimento via PR
- ✅ Rollback grátis (git revert)
- ✅ Escala para 10+ devs, 5+ anos
- ✅ Tokens sob controle (~$0.20/sessão)
- ✅ Grafo de conhecimento emerge naturalmente
- ✅ Backlinks identificam especialistas e impacto

**Trade-offs:**
- ⚠️ Requer disciplina de [[links]] nos arquivos
- ⚠️ Tags obrigatórias em episódios
- ⚠️ Job de consolidation deve rodar mensalmente
- ⚠️ build_graph.py deve rodar após mudanças (ou no /learn)
- ⚠️ Conflitos possíveis em concepts/ (raro, resolvível)

**Métricas de Sucesso:**
- Custo/sessão < $0.50
- Merge conflicts < 5% dos PRs
- Tempo de busca < 5s
- Onboarding de dev novo < 1 semana

### Referências

- Obsidian: https://obsidian.md (modelo de links)
- Zettelkasten: método de notas interconectadas
- Git como database: https://git-scm.com

