# Agent Customization Guide

Referência para Claude ao customizar agents durante o init-engram (Fase 2.5).
O `analyze_project` retorna `customization` por agent; use este guide para aplicar.

## Princípios

- **Nome do arquivo**: sempre `{name}.md` (ex.: `db-expert.md`, não `db-expert-prisma.md`)
- **Conteúdo**: focado na stack do projeto; remover seções irrelevantes
- **Guardrails**: manter regras de segurança e boas práticas

## Input para Customização

Para cada agent em (to_keep ∪ to_create):

1. **Base**: conteúdo atual em `.claude/agents/{name}.md` (instalado ou scaffold)
2. **Stack**: output de `analyze_project` (stack + suggestions)
3. **Customization**: `suggestions.agents[i].customization` quando existir

## Checklist por Campo

### description (frontmatter)
- Incluir stack: "DBA especialista em **Prisma**" ou "Arquiteto especialista em **Next.js**"
- Manter verbos de ação: "Invoque para schema.prisma, migrations..."

### skills (frontmatter)
- Adicionar skills relevantes do `customization.skills`
- Ex.: db-expert + Prisma → `[prisma-workflow]`
- Ex.: architect + Next.js → `[project-analyzer, nextjs-patterns]`

### Body (markdown)
- **variant=prisma**: manter só seções Prisma; remover Drizzle, SQLAlchemy
- **variant=nextjs**: adicionar seção "Next.js" com App Router, Server Components
- **focus**: incluir caminhos do projeto (ex.: `prisma/schema.prisma`, `app/`)
- **remove_sections**: remover seções listadas (ex.: Drizzle, SQLAlchemy)

## Mapeamento por Variant

| Agent | Variant | O que fazer |
|-------|---------|-------------|
| db-expert | prisma | ORM-Specific: só Prisma; focus schema.prisma, migrations; skills: prisma-workflow |
| db-expert | drizzle | ORM-Specific: só Drizzle; focus schema, drizzle-kit; skills: drizzle-workflow |
| architect | nextjs | Seção Next.js: App Router, RSC, Server Actions; skills: nextjs-patterns |
| architect | django | Seção Django: apps, manage.py; skills: django-patterns |
| domain-analyst | generic | Adicionar src_dir; convenções do projeto |
| auth-expert | nextauth | Focus NextAuth, providers, session, middleware; skills: auth-patterns |
| auth-expert | clerk | Focus Clerk, webhooks, orgs; skills: auth-patterns |
| infra-expert | devops | Focus K8s, CI/CD, Terraform; skills: devops-patterns |

## Regras Obrigatórias

- Manter seção "Regras" com NUNCA/SEMPRE
- Manter referência ao cérebro (`brain.add_memory`) quando aplicável
- Manter referência ao skill no frontmatter
- Validar via `validate.py` após escrever
- Registrar via `register.py` após validar

## Exemplo: db-expert + Prisma

**Antes** (genérico): seções Prisma, Drizzle, SQLAlchemy.

**Depois** (customizado):
- description: "DBA especialista em Prisma. Invoque para schema.prisma, migrations, otimização de queries..."
- skills: [prisma-workflow]
- ORM-Specific: **só** seção Prisma
- Adicionar: caminho do schema (prisma/schema.prisma)
- Comandos: `prisma migrate dev`, `prisma migrate deploy`, `prisma studio`
