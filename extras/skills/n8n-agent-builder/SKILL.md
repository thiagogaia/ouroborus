---
name: n8n-agent-builder
description: Construção e otimização de agentes de IA para N8N, especialmente
  agentes de venda via WhatsApp. Use quando precisar criar, modificar ou debugar
  workflows N8N, prompts de agentes, ou sistemas multi-agente de vendas.
  Inclui padrões para Agent Briefing, Agent Classificador, e subagentes.
---

# N8N Agent Builder

Construção de agentes de IA para automação de vendas via N8N + WhatsApp.

## Arquitetura Multi-Agente Padrão

```
Lead (WhatsApp)
  → Agent Briefing (analisa contexto)
  → Agent Classificador (roteia conversa)
  → Subagente Especializado (executa venda)
  → PostgreSQL (persiste estado)
```

### Agent Briefing
- Analisa histórico da conversa e contexto do cliente
- Input: Mensagens anteriores, dados do CRM, estado atual do lead
- Output: Briefing estruturado para o próximo agente
- Regra: NUNCA responde ao cliente, apenas analisa

### Agent Classificador
- Decide qual subagente deve atender
- Critérios: Estágio do funil, tipo de produto, temperatura do lead

### Subagentes de Venda
- Cada um especializado em um cenário (primeiro contato, follow-up, objeção, fechamento)
- Recebe briefing + classificação como contexto

## Estrutura de Prompt N8N

```
## Identidade
[Quem é o agente]

## Contexto
[Dados injetados dinamicamente]

## Objetivo
[O que deve alcançar]

## Regras
[O que PODE e NÃO PODE fazer]

## Formato de Resposta
[Como deve responder]

## Exemplos
[Boas e más respostas]
```

## Padrões para WhatsApp
- Mensagens curtas (máx 3 parágrafos)
- Tom conversacional, não robótico
- Sempre fazer uma pergunta ou CTA
- Lidar com objeções sem ser agressivo

## Integração PostgreSQL
Consulte `references/n8n-postgres-patterns.md` para:
- Expressions corretas (aspas simples para strings)
- UPSERT patterns
- Histórico de mensagens

## Regras
- SEMPRE consulte PATTERNS.md seção "Padrões de Prompt Engineering"
- Mensagens WhatsApp: MÁXIMO 3 parágrafos curtos
- Teste mentalmente o prompt com cenários edge case
- Documente mudanças em PATTERNS.md
