---
id: c6d7c307
title: Modelo de Orquestracao Sequencial
author: "@engram"
date: 2026-02-04
labels: [Concept, Architecture, OrchestrationType]
references: ["[[ADR-003]]", "[[EXP-010]]"]
source_commit: 6d7c3077e102a992d5636709b579e92873723d2e
---

# Modelo de Orquestracao Sequencial

O Engram adota modelo de execucao sequencial **deliberadamente**, nao por limitacao tecnica.

## Vantagens do Modelo Sequencial

1. **Evita race conditions em knowledge files** - multiplos agentes escrevendo simultaneamente causariam conflitos
2. **Permite deteccao confiavel de co-ativacoes** - saber quais skills sao usados juntos na mesma sessao
3. **3x mais barato em tokens** - contexto compartilhado vs contextos isolados por agente
4. **Skills gerados em sequencia evitam redundancia** - genesis sabe o que ja existe

## Por que NAO Implementar Paralelismo

- Context windows isoladas quebrariam o rastreamento de evolucao
- Sem co-ativacoes detectaveis, nao ha dados para propor composicoes
- Arquivos de knowledge conflitariam constantemente
- Custo de tokens triplicaria

## Implicacoes

Esta e uma decisao arquitetural fundamental que sustenta todo o sistema metacircular.
O modelo sequencial permite que o sistema evolua de forma coerente, detectando padroes
de uso e propondo melhorias baseadas em dados reais de co-ativacao.

## Referencias

- [[ADR-003]]: Agents Nao Invocam Outros Agents
- [[EXP-010]]: Analise de Subagentes vs Paralelismo
