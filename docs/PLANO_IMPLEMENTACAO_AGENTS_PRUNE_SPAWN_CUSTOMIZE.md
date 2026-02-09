# Plano de Implementação: Agents — Prune, Spawn, Customize

> Implementação completa: prune_agents.py, integração no init-engram, customização inteligente 100%.

---

## Visão Geral

```
setup.sh (install)     → core + extras (via install_extras.sh)
setup.sh (update)      → core + extras + backup (.claude.bak, CLAUDE.md.bak)
        ↓
/init-engram           → Único comando pós-setup
  Se backup existe: Fase 0.5 (merge + cleanup)
  Fase 2.5 Agents: analyze_project → prune_agents → create → customize
  Fase 3 Skills: generate_component para skills aprovados
```

**Após update**: O usuário roda `/init-engram` — detecta backup, faz merge e cleanup.

---

## Parte 1: prune_agents.py

### 1.1 Localização
`core/genesis/scripts/prune_agents.py`

### 1.2 Interface

`--remove` e `--needed` aceitam lista separada por vírgula (ex.: `db-expert,auth-expert`).

```bash
# Modo 1: Recebe lista explícita de agents a remover (vírgula ou espaços)
python3 prune_agents.py --project-dir . --remove db-expert,auth-expert --output json

# Modo 2: Recebe agents necessários — computa to_remove = existing - needed
python3 prune_agents.py --project-dir . --needed architect,domain-analyst --output json

# Modo 3: Dry-run (só reporta, não remove)
python3 prune_agents.py --project-dir . --needed architect,domain-analyst --dry-run
```

### 1.3 Lógica

1. Listar agents existentes: `.claude/agents/*.md` (nome = stem do arquivo)
2. Se `--remove`: to_remove = lista fornecida
3. Se `--needed`: agents_needed = set(nomes), to_remove = existing - needed
4. Para cada em to_remove:
   - Confirmar que arquivo existe
   - Apagar `.claude/agents/{name}.md`
   - Chamar `register.py --unregister --type agent --name {name}`
5. Output JSON: `{ "removed": [...], "errors": [...] }`

### 1.4 Regras de segurança

- Nunca remover se name não estiver em to_remove
- Se arquivo não existir, só unregister (não falhar)
- Se unregister falhar, reportar em errors mas continuar

### 1.5 Dependências

- `register.py` (subprocess ou import)
- `pathlib` / `os` para listar e apagar

---

## Parte 2: Aprimorar analyze_project.py

### 2.1 Adicionar contexto de customização por agent

Cada sugestão de agent passa a incluir `customization`:

```python
suggestions["agents"].append({
    "name": "db-expert",
    "reason": "Prisma detected — schema design, migrations, query optimization",
    "priority": "high",
    "customization": {
        "variant": "prisma",           # db-expert-prisma em espírito
        "orm": "prisma",
        "skills": ["prisma-workflow"],
        "focus": ["schema.prisma", "migrations", "prisma studio"],
        "remove_sections": ["Drizzle", "SQLAlchemy"]  # ou generic
    }
})
```

### 2.2 Mapeamento de variantes (casos inteligentes)

| Agent | Stack | Variant | Customization |
|-------|-------|---------|---------------|
| db-expert | orm=prisma | prisma | skills: [prisma-workflow], focus Prisma, remover Drizzle/SQLAlchemy |
| db-expert | orm=drizzle | drizzle | skills: [drizzle-workflow], focus Drizzle |
| db-expert | orm=sqlalchemy/django | sqlalchemy | focus SQLAlchemy/Alembic/Django ORM |
| architect | fw=nextjs | nextjs | skills: [nextjs-patterns], focus App Router, Server Components |
| architect | fw=django | django | skills: [django-patterns], focus apps, manage.py |
| architect | fw=fastapi | fastapi | skills: [fastapi-patterns] |
| domain-analyst | qualquer | generic | adicionar src_dir, convenções do projeto |
| auth-expert | auth=nextauth | nextauth | skills: [auth-patterns], focus NextAuth |
| auth-expert | auth=clerk | clerk | skills: [auth-patterns], focus Clerk |
| infra-expert | infra=[k8s,terraform] | devops | skills: [devops-patterns] |

### 2.3 Novos agents no suggest_components

- **auth-expert**: quando `stack.get("auth")`
- **infra-expert**: quando `stack.get("infra")` e len(infra) > 0

### 2.4 Output

O JSON de analyze_project já terá `suggestions.agents` com `customization` opcional. Quem não tiver variant usa "generic".

---

## Parte 3: generate_component.py — Scaffold + customização por Claude

### 3.1 Sem agent-bases

O **core não terá** pasta `agent-bases`. O projeto alvo **não tem** core — só `.claude/`.

**Claude/Cursor** cria agents com base em comandos e inteligência. O setup e init-engram analisam o projeto (tecnologias, conhecimento, padrões) para criar os melhores agents e skills. **Agents e skills são específicos do projeto** — criados no projeto.

### 3.2 Quando agent já existe

Se `.claude/agents/{name}.md` já existe (instalado pelo setup), **não criar** — customizar o existente.

### 3.3 Quando agent não existe (to_create)

`generate_component` usa **scaffold genérico**. A customização é feita pelo Claude usando:
- output de `analyze_project` (stack, technologies, patterns)
- `agent-customization-guide.md`
- Conhecimento do projeto

A inteligência está na **customização**, não em templates pré-definidos.

### 3.4 Origens dos agents instalados

- **core/agents/**: architect, db-expert, domain-analyst → `.claude/agents/` (setup)
- **extras/agents/**: infra-expert, prompt-engineer, **auth-expert** (somente em extras) → `.claude/agents/` (install_extras)

**auth-expert**: criado **apenas** em `extras/agents/auth-expert.md`. Nunca em core/agents.

---

## Parte 4: Customização — 100% Inteligente

### 4.1 Responsável

A customização é feita pelo **Claude** durante o init-engram, guiado por instruções explícitas no comando.

### 4.2 Input para Claude

Para cada agent em (to_keep ∪ to_create):

1. **Base**: conteúdo atual em `.claude/agents/{name}.md` (instalado ou scaffold recém-criado)
2. **Stack**: output de `analyze_project` (stack + suggestions)
3. **Customization**: `suggestions.agents[i].customization` quando existir

### 4.3 Instruções de customização (no init-engram)

```
Para cada agent em [lista]:
1. Ler o conteúdo atual (base ou recém-gerado)
2. Ler customization do analyze_project para este agent
3. Produzir versão customizada:
   - description: incluir stack (ex: "Prisma", "Next.js")
   - skills: frontmatter — adicionar skills relevantes (prisma-workflow, nextjs-patterns)
   - Body: 
     - Se variant=prisma: manter só seções Prisma, remover Drizzle/SQLAlchemy
     - Se variant=nextjs: adicionar seção "Next.js" com App Router, Server Components
     - Incluir caminhos do projeto (src_dir, prisma/schema.prisma)
     - Manter guardrails e regras obrigatórias
4. Escrever em .claude/agents/{name}.md
5. Validar via validate.py
6. Registrar via register.py
```

### 4.4 Reference para Claude

Criar `core/genesis/references/agent-customization-guide.md`:

- Regras de customização por variant
- Exemplos: db-expert Prisma vs Drizzle
- Checklist: description, skills, seções a manter/remover, guardrails

**Importante**: O setup copia `core/genesis/` → `.claude/skills/engram-genesis/`. O guide fica em `.claude/skills/engram-genesis/references/agent-customization-guide.md` no projeto destino. O init-engram usa esse caminho (não existe `core/` no projeto). Ver `docs/ANALISE_AGENT_CUSTOMIZATION_E_INFRA_EXPERT.md`.

### 4.5 Garantia 100%

- O init-engram **obriga** a customização para cada agent
- Validação (validate.py) garante schema
- O reference guide garante que nenhum detalhe seja esquecido

---

## Parte 5: Integração — Fase 2.5 Agents

### 5.1 Onde integrar

A Fase 2.5 **Agents** (prune, create, customize) é integrada em:
- **init-engram**: entre Fase 2 (Plano) e Fase 3 (Skills)

A **Fase 3** do init-engram trata **apenas skills**. Os agents são responsabilidade da Fase 2.5.
(O comando /update-engram foi removido — init-engram faz merge do backup na Fase 0.5.)

### 5.2 Fase 2.5: Agents — Prune, Create, Customize

1. **Análise**
   - Já temos output de analyze_project (Fase 1)
   - agents_needed = [a["name"] for a in suggestions["agents"]]
   - agents_existing = listar `.claude/agents/*.md`

2. **Comparação**
   - to_remove = existing - needed
   - to_keep = existing ∩ needed
   - to_create = needed - existing

3. **Prune**
   ```bash
   python3 .claude/skills/engram-genesis/scripts/prune_agents.py --project-dir . --needed agent1,agent2,... --output json
   ```
   Ou `--remove agent1,agent2,...` com lista explícita. Vírgula como separador.

4. **Create**
   - Para cada em to_create: `generate_component.py --type agent --name X` (scaffold)
   - Sem agent-bases — Claude customiza com inteligência

5. **Customize**
   - Para cada em (to_keep ∪ to_create):
     - Claude lê base, stack, customization
     - Claude lê **`.claude/skills/engram-genesis/references/agent-customization-guide.md`** (referência de customização)
     - Produz conteúdo customizado
     - Escreve, valida, registra

6. **Apresentar ao dev**
   - Removidos: [lista]
   - Criados: [lista]
   - Customizados: [lista com variant quando aplicável]

### 5.3 Atualização do Plano (Fase 2)

Incluir no plano apresentado:

```
Agents:
  Remover: [to_remove]
  Manter e customizar: [to_keep] (variant: prisma, nextjs, etc.)
  Criar e customizar: [to_create]
```

### 5.4 Ordens de execução

- Prune **antes** de Create (evita conflito)
- Create **antes** de Customize (todos os arquivos existem)
- Customize em lote ou um a um (Claude decide)

---

## Parte 6: Casos Inteligentes Detalhados

### 6.1 db-expert + Prisma → "db-expert-prisma"

**Nome do arquivo**: `db-expert.md` (mantém)
**Conteúdo**: Focado 100% em Prisma

- description: "DBA especialista em Prisma. Invoque para schema.prisma, migrations, otimização de queries..."
- skills: [prisma-workflow]
- Body: manter Schema Design, Migrations, Performance
- ORM-Specific: **só** seção Prisma; remover Drizzle, SQLAlchemy
- Adicionar: caminho do schema (prisma/schema.prisma ou similar)
- Comandos: `prisma migrate dev`, `prisma migrate deploy`, `prisma studio`
- Guardrails: manter todos

### 6.2 architect + Next.js

- description: "Arquiteto especialista em Next.js. Invoque para App Router, Server Components..."
- skills: [project-analyzer, nextjs-patterns] (se skill existir)
- Body: adicionar seção "Next.js" com App Router, RSC, Server Actions
- src_dir: app/ ou src/app/

### 6.3 auth-expert (novo, em extras)

- Base: extras/agents/auth-expert.md (instalado via setup)
- Se auth=nextauth: foco em NextAuth, providers, session, middleware
- Se auth=clerk: foco em Clerk, webhooks, orgs

### 6.4 domain-analyst

- Customização leve: adicionar src_dir, convenções de nomenclatura do projeto
- Manter estrutura universal

---

## Parte 7: Setup e Extras

### 7.1 Extras no install e no update

O `setup.sh` reutiliza `install_extras.sh`:

- **Install**: Após core (agents, brain), chama `install_extras.sh "$TARGET_DIR"` — instala agents e skills de extras.
- **Update**: Após atualizar core agents/commands, chama `install_extras.sh "$TARGET_DIR"` — adiciona novos extras, preserva existentes (skip por padrão).

### 7.2 Fluxo de update e backup (unificado)

**Backup unificado** — install e update usam os mesmos nomes:
- `.claude/` → `.claude.bak/`
- `CLAUDE.md` → `CLAUDE.md.bak`

O `migrate_backup.py` detecta `.claude.bak` e `CLAUDE.md.bak`. Implementado em setup.sh.

**Fluxo**:
1. setup --update: cria backups (.claude.bak, CLAUDE.md.bak)
2. Usuário roda **/init-engram**
3. init-engram (Fase 0.5): detecta backup → merge → **apaga backups**
4. init-engram continua com Fase 1 em diante (análise, agents, skills, etc.)

O `migrate_backup.py --cleanup` remove os backups. O init-engram chama isso na Fase 0.5.

### 7.3 Comando /init-engram (único ponto de entrada)

| Cenário | Comportamento |
|---------|---------------|
| **Sem backup** | Fase 1 em diante: análise, agents, skills, knowledge, cérebro |
| **Com backup** | Fase 0.5: merge (agents, skills, knowledge, settings) + cleanup. Brain nunca tocado. Depois Fase 1 em diante. |

### 7.4 Implementado

- [x] setup.sh: chamada a install_extras no install (após brain)
- [x] setup.sh: chamada a install_extras no update (após agents/commands)
- [x] setup.sh: backup unificado (.claude.bak, CLAUDE.md.bak) no update

---

## Parte 8: Ordem de Implementação

| # | Tarefa | Arquivos | Dependências |
|---|--------|----------|--------------|
| 0 | Extras no setup | setup.sh | ✅ Feito |
| 0b | Update: unificar backup para .claude.bak | setup.sh | ✅ Feito |
| 1 | Criar prune_agents.py | core/genesis/scripts/prune_agents.py | register.py |
| 2 | Aprimorar analyze_project: customization | analyze_project.py | — |
| 3 | Aprimorar analyze_project: auth-expert, infra-expert | analyze_project.py | — |
| 4 | Verificar generate_component (já usa scaffold, sem agent-bases) | generate_component.py | — |
| 5 | Criar auth-expert (base) | extras/agents/auth-expert.md | — |
| 6 | Criar agent-customization-guide.md | core/genesis/references/ | — |
| 7 | Integrar Fase 2.5 Agents em init-engram | init-engram.md | 1–6 |
| 8 | ~~update-engram~~ Removido — init-engram faz merge na Fase 0.5 | — | — |

---

## Parte 9: Testes Manuais

### 9.1 Extras no setup

- setup.sh (install) → extras instalados (infra-expert, prompt-engineer, devops-patterns, etc.)
- setup.sh --update → extras atualizados (novos adicionados, existentes preservados)

### 9.2 prune_agents

- Projeto com 3 agents, --needed architect,domain-analyst → db-expert removido
- --dry-run → nenhum arquivo apagado, report correto

### 9.3 Fluxo completo

- Projeto Next.js + Prisma: nenhum remove, db-expert customizado Prisma
- Projeto React puro: db-expert removido
- Projeto com NextAuth: auth-expert criado e customizado

---

## Parte 10: Resumo de Arquivos

| Arquivo | Ação |
|---------|------|
| `setup.sh` | Modificar (extras + backup unificado) — ✅ Feito |
| `core/genesis/scripts/prune_agents.py` | Criar |
| `core/genesis/scripts/analyze_project.py` | Modificar |
| `core/genesis/scripts/generate_component.py` | Verificar (já usa scaffold) |
| `extras/agents/auth-expert.md` | Criar (base) |
| `core/genesis/references/agent-customization-guide.md` | Criar |
| `core/commands/init-engram.md` | Modificar |
| ~~core/commands/update-engram.md~~ | Removido — init-engram único |

---

## Parte 11: Riscos e Mitigações

| Risco | Mitigação |
|-------|-----------|
| Customização inconsistente | Reference guide + checklist obrigatório |
| prune remove agent customizado pelo dev | Aprovação do plano (Fase 2) inclui agents a remover — confirmação implícita |
| Base agent desatualizada | core/agents/ versionado com projeto |
| validate falha após customização | Claude corrige antes de registrar |
| — | Update ajustado para usar `.claude.bak`/`CLAUDE.md.bak` — migrate_backup já funciona. |
