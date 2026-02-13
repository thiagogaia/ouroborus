# Avaliação: Visão setup.sh → init-engram → Evolução

> Avaliação do fluxo ideal vs implementação atual.

---

## 1. Visão Declarada

1. **setup.sh** — Copia tudo (DNA, seeds, comandos, etc.)
2. **/init-engram** — Cria agents, commands, skills e knowledge **contextualizados** para o projeto onde o Engram foi instalado
3. **Evolução** — Criar agents e skills necessárias para o bom andamento do projeto (ao longo do tempo)

---

## 2. O Que o setup.sh Copia (Atual)

| Item | Copiado? | Para onde | Observação |
|------|----------|-----------|------------|
| **DNA** | ✓ | .claude/dna/ | Schemas skill, agent, command, knowledge |
| **Genesis** | ✓ | .claude/skills/engram-genesis | Motor de criação |
| **Evolution** | ✓ | .claude/skills/engram-evolution | Motor de evolução |
| **Seeds** | ✓ | .claude/skills/ | project-analyzer, knowledge-manager, domain-expert, etc. |
| **Agents** | ✓ | .claude/agents/ | architect, db-expert, domain-analyst (3 universais) |
| **Commands** | ✓ | .claude/commands/ | 16 commands universais |
| **Skill templates** | ✓ | .claude/templates/skills/ | nextjs, django, etc. (staging) |
| **Knowledge templates** | ✓ | .claude/knowledge/ | 6 arquivos com ${DATE} substituído |
| **Brain** | ✓ | .claude/brain/ | Grafo, embeddings, scripts |
| **Manifest** | ✓ | .claude/manifest.json | Registro de componentes |
| **CLAUDE.md** | ✓ | raiz | Instruções principais |
| **settings.json** | ✓ | .claude/ | Permissões |

**Conclusão setup:** ✓ Condizente com a visão. O setup copia a base completa.

---

## 3. O Que o /init-engram Cria (Atual)

| Tipo | Cria? | Como | Contextualizado? |
|------|-------|------|------------------|
| **Skills** | ✓ | Genesis: analyze_project sugere → generate_component → Claude customiza | ✓ Sim (templates por stack + customização) |
| **Agents** | ✓ | Genesis: analyze_project sugere → generate_component → Claude customiza | ⚠️ Parcial (scaffold genérico; Claude customiza) |
| **Commands** | ❌ | Não está no plano | — |
| **Knowledge** | ✓ | Populado (estrutura já existe do setup) | ✓ Sim (Claude analisa código e preenche) |

### Detalhamento

**Skills:** O plano da Fase 2 lista "Skills a gerar". O Genesis usa templates quando existem (nextjs-patterns, django-patterns, etc.) ou scaffold genérico. O Claude customiza com padrões do projeto. ✓ Alinhado.

**Agents:** O plano lista "Agents a gerar". O Genesis gera scaffold genérico (tools fixos). O Claude customiza. O analyze_project sugere sempre os mesmos 3 (db-expert, architect, domain-analyst) + variação por ORM. ⚠️ Funciona, mas poderia ser mais contextualizado (auth-expert para NextAuth, etc.).

**Commands:** O init-engram **não inclui commands no plano**. A Fase 3 diz "Commands: adaptar para o package manager e scripts do projeto" — isso se refere a **customizar os 16 commands já copiados**, não a **criar commands novos** contextualizados (ex: /deploy, /migrate). ❌ Gap.

**Knowledge:** A estrutura vem do setup (6 arquivos). O init-engram Fase 4 **popula** com conteúdo (PATTERNS, DOMAIN, PRIORITY_MATRIX, etc.) baseado em análise do código. ✓ Alinhado.

---

## 4. Evolução — Criar Agents e Skills Necessárias

| Aspecto | Visão | Atual | Gap |
|---------|-------|-------|-----|
| **Propor novo skill** | Evolution detecta padrão → propõe → Genesis cria | Evolution SKILL descreve o fluxo; depende de Claude "notar" padrão 3+ vezes | ⚠️ Não há detecção automática |
| **Propor novo agent** | Evolution detecta necessidade → propõe → Genesis cria | Evolution foca em skills; não há "propor agent" explícito | ❌ Gap |
| **Tracking de uso** | Dados de uso alimentam propostas | register --activate e co_activation --log-session são manuais | ❌ Dados não fluem |
| **/create sob demanda** | Dev ou sistema cria quando precisa | /create existe; funciona | ✓ OK |
| **Evolution → Genesis** | Proposta aprovada → Genesis gera | "Se aprovado → invocar engram-genesis" | ✓ Fluxo descrito |

### Resumo Evolução

A **capacidade** existe (Genesis cria, Evolution propõe, /create sob demanda). Os **gaps** são:

1. **Tracking manual** — Ninguém chama register --activate nem co_activation consistentemente.
2. **Evolution não propõe agents** — Só skills.
3. **Detecção de padrão** — Depende de Claude "notar"; não há métrica automática.

---

## 5. Avaliação Geral

### Alinhado com a visão

| Item | Status |
|------|--------|
| setup.sh copia base completa | ✓ |
| init-engram cria skills contextualizados | ✓ |
| init-engram cria agents (com customização) | ✓ |
| init-engram popula knowledge | ✓ |
| /create para criar sob demanda | ✓ |
| Evolution propõe skills → Genesis cria | ✓ (fluxo descrito) |

### Parcialmente alinhado

| Item | Status |
|------|--------|
| Agents contextualizados | ⚠️ Scaffold genérico; customização manual |
| Evolução ao longo do tempo | ⚠️ Falta tracking automático |

### Não alinhado

| Item | Status |
|------|--------|
| init-engram cria **commands** contextualizados | ❌ Commands não estão no plano; não há geração |
| Evolution propõe **agents** | ❌ Só skills |
| Dados de uso para evolução | ❌ Manuais |

---

## 6. Ajustes Recomendados para Alinhar à Visão

### 6.1 init-engram — Incluir Commands

**Problema:** Commands não são gerados no init-engram.

**Solução:**
1. **analyze_project.py** — Adicionar sugestão de commands (ex: deploy se docker, migrate se ORM, test se testing).
2. **init-engram Fase 2** — Incluir "Commands a gerar" no plano.
3. **init-engram Fase 3** — Para cada command aprovado: generate_component --type command --name X.

### 6.2 Evolution — Incluir Agents

**Problema:** Evolution só propõe skills.

**Solução:**
1. **engram-evolution SKILL** — Adicionar seção "Propor Novo Agent" (ex: "db-expert muito usado e auth não existe → propor auth-expert").
2. **track_usage / curriculum** — Considerar agents no relatório de gaps.

### 6.3 Evolução — Tracking Automático

**Problema:** Dados de uso não fluem.

**Solução:**
1. **session_summary.py** — Script que recebe lista de componentes usados e chama register + co_activation.
2. **/learn Fase 5** — Exigir que Claude declare componentes usados → pipe para session_summary.

---

## 7. Resumo Executivo

| Visão | Implementação | Ação |
|------|---------------|------|
| setup copia tudo | ✓ Sim | Nenhuma |
| init-engram cria skills contextualizados | ✓ Sim | Nenhuma |
| init-engram cria agents contextualizados | ⚠️ Parcial | Melhorar scaffold/catálogo |
| init-engram cria **commands** contextualizados | ❌ Não | Adicionar ao plano + analyze_project |
| init-engram popula knowledge | ✓ Sim | Nenhuma |
| Evoluir: criar agents e skills | ⚠️ Parcial | Tracking + Evolution propor agents |

**Conclusão:** O fluxo está **70% alinhado**. Os principais gaps: (1) commands contextualizados no init-engram, (2) Evolution propor agents, (3) tracking automático para evolução real.
