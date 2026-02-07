# 🐍 Engram v2 — Guia de Uso Completo

## Índice

1. [Ciclo de Vida](#ciclo-de-vida)
2. [Metodologia Diária](#metodologia-diária)
3. [Exemplo 1: Instalando num SaaS Next.js](#exemplo-1-instalando-num-saas-nextjs)
4. [Exemplo 2: Instalando num Backend Python](#exemplo-2-instalando-num-backend-python)
5. [Exemplo 3: Auto-geração em ação](#exemplo-3-auto-geração-em-ação)
6. [Exemplo 4: O sistema evoluindo sozinho](#exemplo-4-o-sistema-evoluindo-sozinho)
7. [Exemplo 5: Conhecimento viajando entre projetos](#exemplo-5-conhecimento-viajando-entre-projetos)
8. [Referência Rápida](#referência-rápida)

---

## Ciclo de Vida

O Engram tem 3 fases distintas. A maioria do tempo você vive na fase 3.

```
FASE 1: Instalação (uma vez)
  setup.sh → detecta stack → instala DNA + seeds

FASE 2: Inicialização (uma vez)
  /init-engram → Claude analisa o projeto → gera skills/agents → popula knowledge

FASE 3: Uso Diário (todo dia)
  /status → trabalha → /learn → próxima sessão sabe onde parou
```

---

## Metodologia Diária

### Ao abrir o Claude Code

```
> /status
```

O Claude lê CURRENT_STATE.md, PRIORITY_MATRIX.md e o git log. Ele já sabe:
- O que foi feito ontem
- O que é prioridade agora
- Que bloqueios existem
- Qual a próxima ação concreta

Você não precisa explicar nada. Ele sabe.

### Ao começar uma feature

```
> /plan implementar sistema de notificações por email
```

O Claude consulta os knowledge files (padrões existentes, decisões passadas, regras de domínio, experiências anteriores) e gera um plano de steps concretos com estimativa de complexidade e riscos.

Se o plano envolve decisão arquitetural, ele já sugere registrar no ADR_LOG.

### Durante o trabalho

Trabalhe normalmente. O Claude já sabe quais padrões seguir (PATTERNS.md), quais termos usar (DOMAIN.md), e quais prioridades existem (PRIORITY_MATRIX.md).

Se precisar de code review antes de commitar:

```
> /review
```

Se precisar de uma segunda opinião sobre arquitetura, o Claude ativa o subagente `architect`. Se for questão de banco de dados, ativa o `db-expert`. Você não precisa pedir — ele sabe quando ativar.

### Ao commitar

```
> /commit
```

Gera mensagem semântica baseada nas mudanças reais.

### Ao finalizar a sessão (IMPORTANTE)

```
> /learn
```

Este é **o comando mais importante**. Ele:

1. Analisa o que mudou (git diff + commits)
2. Reflete: que padrões surgiram? que decisões foram tomadas?
3. Atualiza TODOS os knowledge files relevantes
4. Registra quais skills foram usados (tracking)
5. Detecta se skills estão sendo usados sempre juntos (co-ativação)
6. Propõe evoluções: novo skill? composição? aposentar algo?

**Se você não roda `/learn`, a próxima sessão começa sem saber o que aconteceu.**

### Periodicamente (a cada ~10 sessões)

```
> /doctor
```

Health check completo: estrutura ok? knowledge fresco? skills registrados? algo stale?

```
> /curriculum
```

Mostra a cobertura de skills do projeto. Sugere o que criar para preencher gaps.

---

## Exemplo 1: Instalando num SaaS Next.js

Cenário: você tem um SaaS de gerenciamento de clínicas médicas usando Next.js 14, Prisma, PostgreSQL, shadcn/ui, Better Auth.

### Terminal (fora do Claude)

```bash
# Clone o Engram
git clone https://github.com/your-user/engram.git ~/engram

# Instale no seu projeto
cd ~/engram
./setup.sh /home/dev/clinica-saas
```

Output:

```
═══════════════════════════════════════════════════════════
  🐍 Engram v2.0.0 — Persistent Memory for Claude Code
═══════════════════════════════════════════════════════════

[15:20:01] ▸ Analisando projeto em: /home/dev/clinica-saas

  Stack Detectada:
    ✓ Node.js (pnpm)
    ✓ Framework: nextjs v14.2.0
    ✓ ORM: prisma
    ✓ Database: postgresql
    ✓ TypeScript
    ✓ Docker

[15:20:01] ✓ Schemas instalados (DNA do sistema)
[15:20:01] ✓ Genesis skill instalado (motor de auto-geração)
[15:20:01] ✓ Evolution skill instalado (motor de evolução)
[15:20:01] ✓ Seeds universais instalados
[15:20:01] ✓ Agents universais instalados
[15:20:01] ✓ Commands instalados (12 commands)
[15:20:01] ✓ Knowledge templates inicializados (6 arquivos)
[15:20:01] ✓ Manifest inicializado
[15:20:01] ✓ CLAUDE.md gerado
[15:20:01] ✓ settings.json customizado
[15:20:01] ✓ Knowledge inicializado

  ✅ Engram v2.0.0 Instalado!

  Próximo passo:
    cd /home/dev/clinica-saas
    claude
    /init-engram
```

### No Claude Code

```
> /init-engram
```

O Claude faz 6 coisas automaticamente:

**1. Analisa o projeto:**
```
🐍 Engram Init — Análise do Projeto
═══════════════════════════════════════
Stack: Next.js 14 + Prisma + PostgreSQL + shadcn + Better Auth
Módulos detectados: 14 (auth, dashboard, patients, appointments, billing...)
Padrões no código: Server Components, Server Actions, Zod validation
Entidades no Prisma: Patient, Appointment, Doctor, Clinic, Invoice, Plan
```

**2. Apresenta plano de geração:**
```
Skills a gerar:
  🔴 nextjs-patterns — Server Components, App Router, caching
  🔴 prisma-workflow — migrations, queries, schema design
  🟡 auth-patterns — Better Auth flows, session handling
  🟡 billing-patterns — Stripe/payment integration patterns

Agents já instalados:
  ✅ architect, domain-analyst, db-expert

Seeds já instalados:
  ✅ project-analyzer, knowledge-manager, domain-expert,
     priority-engine, code-reviewer, engram-factory

Gerar esses 4 skills? (confirma)
```

**3. Auto-gera os skills aprovados** usando genesis:

Para cada skill:
- `generate_component.py` cria o scaffold
- Claude lê o código real do projeto e preenche o SKILL.md com padrões concretos (não genéricos)
- `validate.py` valida contra o schema
- `register.py` registra no manifest

Exemplo do que `nextjs-patterns/SKILL.md` gerado contém:

```markdown
---
name: nextjs-patterns
description: Padrões Next.js 14 App Router para o projeto clinica-saas.
  Use quando criar páginas, componentes, Server Actions, ou configurar
  caching e metadata. Inclui padrões específicos de multi-tenant por clínica.
---

# Next.js Patterns — clinica-saas

## Server Components (padrão)
- Todas as páginas são Server Components
- Client Components apenas para: forms, modals, dropdowns, real-time
- Padrão: 'use client' SEMPRE no topo, NUNCA no meio

## Server Actions
- Definir em `src/server/actions/[domínio].ts`
- Padrão do projeto: Zod schema → validate → prisma → revalidate
- SEMPRE revalidatePath após mutation

## Estrutura de Rotas
- Route groups: (auth), (dashboard), (public)
- Layout por group com proteção de sessão
- Padrão de metadata: generateMetadata() em todas as páginas

## Multi-Tenant
- Clínica identificada por subdomain (middleware.ts)
- Todas as queries filtram por clinicId
- NUNCA esquecer WHERE clinicId = ...
```

**4. Popula knowledge files** com dados reais:

- `CURRENT_STATE.md`: mapeamento de todos os 14 módulos, dívidas técnicas, estado de cada área
- `PATTERNS.md`: 12 padrões extraídos do código real (naming conventions, error handling, etc)
- `DOMAIN.md`: glossário médico (Paciente, Consulta, Prontuário, Plano, Convênio...) + 8 regras de negócio
- `PRIORITY_MATRIX.md`: 6 TODOs encontrados no código, priorizados com ICE Score
- `EXPERIENCE_LIBRARY.md`: vazia (será populada pelo /learn)

**5. Roda `/doctor`:**
```
🟢 Health Score: 100%
  ✅ 30 ok  |  ⚠️ 0 warnings  |  ❌ 0 errors
```

**6. Relatório final:**
```
🐍 Engram Init Completo!
═══════════════════════════════════════
  ✅ 4 skills gerados e validados
  ✅ 3 agents disponíveis
  ✅ 6 knowledge files populados
  ✅ Doctor: 100%

  💡 Próxima ação: resolver "API de agendamento não valida conflito
     de horário" (ICE: 27, prioridade #1)
```

A partir daqui, toda nova sessão do Claude já sabe tudo sobre o projeto.

---

## Exemplo 2: Instalando num Backend Python

Cenário: API REST com Django + DRF + PostgreSQL + Celery + Docker.

### Terminal

```bash
./setup.sh /home/dev/logistics-api
```

O setup detecta:
```
Stack Detectada:
  ✓ Python
  ✓ Framework: django
  ✓ Database: postgresql
  ✓ Docker
```

Gera CLAUDE.md com regras de Python/Django (sem TypeScript, sem npm).
O settings.json inclui permissões para `pip`, `python3`, `python`.

### No Claude Code

```
> /init-engram
```

Desta vez o `analyze_project.py` sugere:

```
Skills a gerar:
  🔴 django-patterns — models, views, serializers, management commands
  🔴 celery-workflow — tasks, scheduling, error handling
  🟡 drf-patterns — serializers, viewsets, permissions, pagination
  🟡 docker-workflow — compose management, build optimization
```

O Claude gera `django-patterns` com padrões do código real:

```markdown
## Models
- Todos herdam de BaseModel (created_at, updated_at, is_active)
- Soft delete via is_active=False (nunca delete() real)
- Manager customizado: objects = ActiveManager() (filtra is_active=True)

## Views
- Padrão: ViewSets no DRF, nunca function-based views
- Permissões: IsAuthenticated + custom (IsCompanyMember)
- Paginação: LimitOffsetPagination com default=20

## Celery Tasks
- @shared_task(bind=True, max_retries=3, default_retry_delay=60)
- Naming: [app]_[ação] (e.g. shipments_calculate_route)
- SEMPRE idempotente — replay não causa side effects
```

O `DOMAIN.md` é populado com glossário de logística: Remessa, Rota, Transportadora, CTe, NF-e, Prazo de Entrega...

---

## Exemplo 3: Auto-geração em ação

Cenário: 3 semanas depois, trabalhando no clinica-saas. Você precisa de funcionalidade que não existe.

### Criando skill sob demanda

```
> /create skill appointment-validator
```

O Claude ativa `engram-genesis` e:

1. Consulta o schema (`skill.schema.md`)
2. Gera scaffold via `generate_component.py`
3. Pergunta: "Qual o propósito deste skill?"
4. Você: "Validar regras complexas de agendamento — conflito de horário, tempo mínimo entre consultas, horário de funcionamento"
5. Claude lê o código de agendamento existente e preenche:

```markdown
---
name: appointment-validator
description: Validação de regras de agendamento médico. Use quando criar ou
  modificar lógica de agendamento para garantir que conflitos de horário,
  intervalo mínimo e horário de funcionamento são respeitados.
---

# Appointment Validator

## Regras de Negócio (extraídas de DOMAIN.md)
- RN-003: Mínimo 15min entre consultas do mesmo médico
- RN-004: Horário de funcionamento por clínica (config no banco)
- RN-007: Paciente não pode ter 2 consultas no mesmo horário

## Workflow de Validação
1. Receber: doctorId, patientId, startTime, endTime
2. Verificar conflito de médico (query com overlap)
3. Verificar conflito de paciente
4. Verificar intervalo mínimo
5. Verificar horário de funcionamento da clínica
6. Retornar: { valid: boolean, violations: string[] }

## Padrão de Query (conflito de horário)
SELECT EXISTS (
  SELECT 1 FROM appointments
  WHERE doctor_id = $1
    AND status NOT IN ('cancelled', 'no_show')
    AND tsrange(start_time, end_time) && tsrange($2, $3)
)
```

6. Valida: `✅ skill appointment-validator is valid`
7. Registra no manifest: `✅ Registered skill 'appointment-validator' (v1.0.0, source: genesis)`

Agora toda vez que você trabalha com agendamento, o Claude consulta esse skill automaticamente.

### Criando agent sob demanda

```
> /create agent compliance-checker
```

Claude gera um agent especializado em conformidade da clínica (LGPD, ANVISA, CFM):

```markdown
---
name: compliance-checker
description: Verificador de conformidade médica e LGPD. Invoque quando
  trabalhar com dados sensíveis de pacientes, prontuários, ou integrações
  com sistemas de saúde.
tools:
  - Read
  - Grep
  - Glob
---

Você é um especialista em conformidade de sistemas de saúde.

## Responsabilidades
- Verificar que dados de pacientes estão protegidos (LGPD)
- Garantir que prontuários seguem padrões do CFM
- Validar que logs de acesso existem para dados sensíveis
- Verificar criptografia de dados em repouso e trânsito

## Checklist
- [ ] Campos sensíveis (CPF, diagnóstico) são criptografados?
- [ ] Existe log de acesso para visualização de prontuário?
- [ ] Dados podem ser exportados/deletados (LGPD)?
- [ ] Backup de prontuários segue retenção mínima de 20 anos?
```

### Criando command sob demanda

```
> /create command deploy
```

Claude gera um command customizado para o fluxo de deploy do projeto:

```markdown
Preparar e executar deploy para produção.

## Checklist pré-deploy
1. `pnpm run build` — sucesso?
2. `pnpm run test` — todos passam?
3. `pnpm run lint` — sem erros?
4. `npx prisma migrate status` — migrations sincronizadas?
5. Variáveis de ambiente configuradas?
6. Git: estamos na branch main? Tudo commitado?

## Deploy
1. Criar tag: git tag -a v[version] -m "[mensagem]"
2. Push: git push origin main --tags
3. Vercel auto-deploya ou: [comando manual]

## Pós-deploy
1. Smoke test: [URLs críticas]
2. Se falhar: rollback para tag anterior
3. Registrar em CURRENT_STATE.md
```

---

## Exemplo 4: O sistema evoluindo sozinho

Cenário: 6 semanas de uso do Engram. O `/learn` vem sendo rodado toda sessão.

### Sessão 37: O `/learn` detecta co-ativação

```
> /learn
```

O Claude analisa e reporta:

```
🔄 Evolução do Sistema
═══════════════════════

📊 Co-ativação detectada:
  🔗 appointment-validator + db-expert — 8 sessões (72%)
     💡 Considere: esses dois sempre trabalham juntos.
        Criar skill composto "appointment-pipeline"?

📦 Componente stale:
  🟡 docker-workflow — 0 usos em 37 sessões
     Aposentar? (o projeto faz deploy via Vercel, Docker é só local)

📈 Skills mais usados:
  1. nextjs-patterns — 34 ativações
  2. prisma-workflow — 28 ativações
  3. appointment-validator — 15 ativações
```

Você diz: "Sim, cria o pipeline e aposenta o docker."

Claude executa:

```bash
# 1. Cria skill composto
python3 .claude/skills/engram-genesis/scripts/generate_component.py \
  --type skill --name appointment-pipeline --project-dir .
```

Customiza com `composes: [appointment-validator, db-expert]`:

```markdown
---
name: appointment-pipeline
description: Pipeline completo para operações de agendamento. Orquestra
  validação de regras de negócio e otimização de queries. Use quando
  trabalhar com criação, edição ou cancelamento de consultas.
composes:
  - appointment-validator
  - db-expert
---

# Appointment Pipeline

## Workflow
1. Ativar appointment-validator → validar regras de negócio
2. Ativar db-expert → otimizar queries de overlap e índices
3. Implementar operação com ambos os contextos ativos

## Quando Usar
- Criar nova consulta
- Reagendar consulta existente
- Relatórios de agenda com queries complexas
```

```bash
# 2. Aposenta docker-workflow
python3 .claude/skills/engram-evolution/scripts/archive.py \
  --type skill --name docker-workflow --project-dir .

# 📦 Archived skill 'docker-workflow' v1.0.0 → .claude/versions/
```

### Sessão 45: O sistema evolui um skill existente

O Claude nota que nas últimas 5 sessões, toda vez que ativa `nextjs-patterns`, ele adiciona instruções extras sobre caching com `unstable_cache`. Ele propõe:

```
💡 Notei que você pede instruções de caching com unstable_cache em
   quase toda sessão com nextjs-patterns. Incorporar direto no skill?
```

Você: "Sim."

Claude:
1. Faz backup: `archive.py --type skill --name nextjs-patterns`
2. Adiciona seção de caching no SKILL.md
3. Version bump: `1.0.0 → 1.1.0`
4. Registra no evolution-log.md

### Sessão 60: `/curriculum` mostra maturidade

```
> /curriculum
```

```
📚 Engram Curriculum
══════════════════════════════════
  🟢 Skill Coverage: 95%
  Installed: 14 skills

  🎯 Missing Skills (1):
    🔴 test-patterns (quality)
       Test writing patterns
       → /create skill test-patterns

  ✅ Full agent coverage

  ⚠️ Usage Gaps (1):
    📦 priority-engine — 2 usos em 60 sessões
       Consider: realmente precisa existir como skill separado?
```

---

## Exemplo 5: Conhecimento viajando entre projetos

Cenário: você terminou o clinica-saas e vai começar um novo projeto — um SaaS de gerenciamento de academia (gym-saas). Quer reaproveitar skills que funcionaram.

### No clinica-saas

```
> /export skill nextjs-patterns
> /export skill prisma-workflow
> /export pattern PAT-003
> /export experience EXP-001
```

```
✅ Exported skill 'nextjs-patterns' to ~/.engram/skills/
✅ Exported skill 'prisma-workflow' to ~/.engram/skills/
✅ Exported pattern 'PAT-003' to ~/.engram/patterns.json
✅ Exported experience 'EXP-001' to ~/.engram/experiences.json
```

### Instalar Engram no gym-saas

```bash
./setup.sh /home/dev/gym-saas
```

### No Claude Code do gym-saas

```
> /init-engram
```

O Claude analisa o projeto e gera skills customizados. Mas antes de criar `nextjs-patterns` do zero, ele verifica:

```
> /import nextjs-patterns
```

```
🌐 Importing from global memory:
  📦 nextjs-patterns (from: clinica-saas)

  ✅ Imported to .claude/skills/nextjs-patterns/
  ✅ Registered in manifest (source: global)

  ⚠️ Este skill veio de outro projeto. Customize:
     - Remover padrões específicos de multi-tenant por clínica
     - Adaptar para entidades de academia (Aluno, Plano, Treino)
     - Manter padrões gerais de Next.js (Server Components, Actions)
```

O Claude então adapta o SKILL.md importado, removendo regras de clínica e adicionando regras de academia. O skill começa 80% pronto em vez de do zero.

```
> /import prisma-workflow
```

Mesmo processo. O Claude adapta queries de exemplo para entidades de academia.

### A memória global acumula

Com o tempo, `~/.engram/` vira uma biblioteca pessoal:

```
> /export
```

```
🌐 Engram Global Memory (~/.engram/)
══════════════════════════════════════

  🎯 Skills (6):
    📦 nextjs-patterns (from: clinica-saas)
    📦 prisma-workflow (from: clinica-saas)
    📦 appointment-validator (from: clinica-saas)
    📦 drf-patterns (from: logistics-api)
    📦 celery-workflow (from: logistics-api)
    📦 gym-membership-rules (from: gym-saas)

  📝 Patterns (4):
    PAT-003: Padrão de Server Action com Zod (clinica-saas)
    PAT-007: Padrão de Celery task idempotente (logistics-api)
    PAT-011: Padrão de webhook handler (gym-saas)
    PAT-012: Padrão de migration zero-downtime (logistics-api)

  💡 Experiences (3):
    EXP-001: Como migrar de pages/ para app/ router (clinica-saas)
    EXP-004: Como configurar Celery com Redis em Docker (logistics-api)
    EXP-006: Como implementar multi-tenant com middleware (clinica-saas)
```

Cada novo projeto começa mais rápido porque você importa o que já funcionou.

---

## Referência Rápida

### Commands do dia a dia

| Quando | Comando | O que faz |
|--------|---------|-----------|
| Início da sessão | `/status` | Estado, prioridades, próxima ação |
| Antes de implementar | `/plan [feature]` | Plano de steps com riscos |
| Antes de commitar | `/review` | Code review dos arquivos alterados |
| Ao commitar | `/commit` | Mensagem semântica automática |
| **Final da sessão** | **`/learn`** | **Registra tudo + evolui o sistema** |
| Quando reprioritizar | `/priorities` | ICE Score + desprioritização |
| Criar componente | `/create [tipo] [nome]` | Auto-gera skill/agent/command |
| Health check | `/doctor` | Valida estrutura + freshness |
| Cobertura de skills | `/curriculum` | Gaps + sugestões |
| Compartilhar entre projetos | `/export` / `/import` | Memória global |

### Fluxo visual do dia

```
  ┌─────────────────────────────────────────┐
  │  /status                                │
  │  → "prioridade #1: X, bloqueio: nenhum" │
  └──────────────┬──────────────────────────┘
                 │
  ┌──────────────▼──────────────────────────┐
  │  /plan [feature]                        │
  │  → plano com 5 steps                    │
  └──────────────┬──────────────────────────┘
                 │
  ┌──────────────▼──────────────────────────┐
  │  Trabalha normalmente                   │
  │  (Claude consulta skills automaticam.)  │
  └──────────────┬──────────────────────────┘
                 │
  ┌──────────────▼──────────────────────────┐
  │  /review                                │
  │  → "2 issues, 1 sugestão"              │
  └──────────────┬──────────────────────────┘
                 │
  ┌──────────────▼──────────────────────────┐
  │  /commit                                │
  │  → "feat(appointments): add validation" │
  └──────────────┬──────────────────────────┘
                 │
  ┌──────────────▼──────────────────────────┐
  │  /learn          ← NÃO ESQUEÇA!        │
  │  → atualiza knowledge                   │
  │  → registra uso de skills               │
  │  → propõe evoluções                     │
  └──────────────┬──────────────────────────┘
                 │
                 🐍 próxima sessão sabe tudo
```

### O que NÃO fazer

- **Não pular o `/learn`** — sem ele a próxima sessão perde contexto
- **Não editar knowledge files manualmente** — deixe o Claude fazer via `/learn`
- **Não criar skills manualmente** — use `/create` para validação automática
- **Não deletar skills** — use `/learn` para propor archive (mantém backup)
- **Não ignorar o `/doctor`** — ele pega problemas antes que virem dor de cabeça

### O que commitar no git

**Tudo.** O `.claude/` inteiro é versionável:

```gitignore
# NÃO adicione ao .gitignore:
# .claude/           ← versione TUDO
# CLAUDE.md          ← versione
```

Knowledge files no git = histórico de como o projeto evoluiu.
Outro dev com Engram instalado herda todo o conhecimento.