# Genesis — Funcionamento Detalhado e Gaps

> Análise do motor de auto-geração do Engram: scripts, fluxo, templates e lacunas.

---

## 1. O Que É o Genesis

O Genesis é o **motor de criação** — gera skills, agents e commands customizados para o projeto. É invocado por:
- **/init-engram** — geração em lote no "start" do projeto
- **/create [tipo] [nome]** — geração sob demanda

O Genesis **não gera knowledge files** — a estrutura knowledge/ vem do setup.sh (templates/knowledge/). O Genesis **popula** o conteúdo (PATTERNS, DOMAIN, etc.) durante o init-engram Fase 4.

---

## 2. Estrutura do Genesis

```
core/genesis/
├── SKILL.md                 # Workflow para Claude
├── scripts/
│   ├── analyze_project.py   # Detecta stack → sugere componentes
│   ├── generate_component.py # Gera scaffold (skill/agent/command)
│   ├── validate.py           # Valida contra DNA
│   ├── register.py          # Registra no manifest
│   ├── compose.py           # Resolve cadeias composes:
│   └── migrate_backup.py    # Migração de backups (upgrade)
└── references/
    ├── skill-patterns.md    # Padrões de workflow
    ├── anti-patterns.md     # O que evitar
    └── claude_cerebro_section.md  # Bloco para CLAUDE.md
```

---

## 3. Fluxo de Funcionamento

### 3.1 /init-engram (modo completo)

```
Fase 0: migrate_backup (se backup existe)
        ↓
Fase 1: analyze_project.py --output json
        → stack detectada
        → suggestions: { skills: [...], agents: [...] }
        ↓
Fase 2: Apresentar plano ao dev
        ↓
Fase 3: Para cada componente aprovado:
        1. generate_component.py --type X --name Y
        2. Claude customiza (usa DNA + skill-patterns)
        3. validate.py --type X --path ...
        4. register.py --type X --name Y --source genesis
        ↓
Fase 4: Popular knowledge (manual via Claude)
        → PATTERNS, DOMAIN, PRIORITY_MATRIX, etc.
        → brain.add_memory() para estado inicial
        ↓
Fase 5–7: populate cérebro, doctor, cleanup
```

### 3.2 /create [tipo] [nome] (modo sob demanda)

```
1. Validar tipo (skill|agent|command)
2. Validar nome kebab-case
3. Verificar se já existe
4. generate_component.py
5. Claude customiza
6. validate.py
7. register.py
```

### 3.3 Fluxo de Templates (skills apenas)

```
setup.sh
  → cp templates/skills/* → .claude/templates/skills/

generate_component.py --type skill --name nextjs-patterns
  → Busca .claude/templates/skills/**/nextjs-patterns.skill.tmpl
  → Se encontra: copia como SKILL.md, remove template
  → Se não: gera scaffold genérico

init-engram Fase 7
  → rm -rf .claude/templates/
```

---

## 4. Detalhamento por Script

### 4.1 analyze_project.py

| Função | Entrada | Saída |
|--------|---------|-------|
| detect_stack() | project_dir | languages, framework, orm, database, ui, auth, testing, infra, pkg_manager |
| suggest_components() | stack | skills[], agents[], commands[], reasoning[] |

**Skills sugeridos:** framework-patterns, ORM-workflow, test-patterns, auth-patterns, docker-workflow, devops-patterns, typescript-strict

**Agents sugeridos:** db-expert (se ORM/DB), architect (sempre), domain-analyst (sempre)

**Commands sugeridos:** Nenhum. O suggest_components não retorna commands.

**Stack detectada:** Node, Python, PHP, Rust, Go, Ruby; Next.js, Django, FastAPI, NestJS, Laravel, Rails, Flask, Express, Fastify, Vue, React, Angular, SvelteKit; Prisma, Drizzle, TypeORM, Sequelize, Mongoose; PostgreSQL, MySQL, MongoDB, SQLite; shadcn, MUI, Chakra; NextAuth, Clerk, Better Auth, Lucia; Vitest, Jest, Playwright; Docker, K8s, GitHub Actions, Terraform, ArgoCD.

### 4.2 generate_component.py

| Tipo | Template? | Scaffold |
|------|------------|----------|
| **skill** | Busca .claude/templates/skills/**/{name}.skill.tmpl | Se não achar: genérico com TODO |
| **agent** | Não tem templates | Sempre genérico: tools Read/Grep/Glob, description placeholder |
| **command** | Não tem templates | Sempre genérico: 5 linhas com TODO |

**load_project_context():** Lê manifest, package.json, detecta framework/orm/stack. Usado para inscrever "Stack detectada: X" no scaffold.

**Knowledge:** Não há generate para knowledge. O Genesis SKILL diz "knowledge.schema.md para knowledge files" mas não existe generate_component --type knowledge.

### 4.3 validate.py

Valida contra regras do DNA. Ver `docs/DNA_DETALHADO.md` para cobertura.

### 4.4 register.py

Registra no manifest.json: version, source, created_at, activations, last_used, health.

### 4.5 compose.py

Não faz parte do fluxo de geração. Usado por:
- **/doctor** — `compose.py --graph` para mostrar grafo de composição
- **engram-factory** — resolver cadeia quando skill tem composes:

Resolve dependências, detecta ciclos, gera plano de ativação.

### 4.6 migrate_backup.py

Para upgrades: detecta .claude.bak/ e CLAUDE.md.bak, analisa, migra componentes customizados e knowledge.

---

## 5. Templates Disponíveis

| Template | Framework | Match no generate |
|----------|-----------|-------------------|
| nextjs-patterns.skill.tmpl | Next.js | nextjs-patterns ✓ |
| django-patterns.skill.tmpl | Django | django-patterns ✓ |
| fastapi-patterns.skill.tmpl | FastAPI | fastapi-patterns ✓ |
| nestjs-patterns.skill.tmpl | NestJS | nestjs-patterns ✓ |
| express-patterns.skill.tmpl | Express | express-patterns ✓ |
| react-patterns.skill.tmpl | React | react-patterns ✓ |
| vue-patterns.skill.tmpl | Vue | vue-patterns ✓ |
| angular-patterns.skill.tmpl | Angular | angular-patterns ✓ |
| laravel-patterns.skill.tmpl | Laravel | laravel-patterns ✓ |
| rails-patterns.skill.tmpl | Rails | rails-patterns ✓ |
| flask-patterns.skill.tmpl | Flask | flask-patterns ✓ |

**Sem template (sempre scaffold genérico):**
- prisma-workflow, drizzle-workflow
- test-patterns, auth-patterns
- docker-workflow, devops-patterns
- typescript-strict
- Qualquer agent
- Qualquer command

---

## 6. Gaps Identificados

### 6.1 analyze_project.py

| # | Gap | Impacto |
|---|-----|---------|
| G1 | **Não sugere commands** | Projetos que precisam de /deploy, /migrate não recebem sugestão |
| G2 | **Agents sempre os mesmos 3** | Sem auth-expert, k8s-expert, etc. por stack |
| G3 | **Sugestões podem não ter template** | prisma-workflow, auth-patterns sugeridos mas sem .skill.tmpl → scaffold vazio |
| G4 | **Não considera skills já instalados** | Pode sugerir nextjs-patterns quando seeds já têm |
| G5 | **devops-patterns tem source: "extras"** | Sugere instalar de extras; init-engram não faz install de extras |

### 6.2 generate_component.py

| # | Gap | Impacto |
|---|-----|---------|
| G6 | **Agent scaffold genérico** | Não usa contexto (Prisma, NextAuth); tools sempre Read/Grep/Glob |
| G7 | **Command scaffold muito fraco** | 5 linhas; sem padrões (status, plan, deploy) |
| G8 | **Sem --type knowledge** | Genesis SKILL menciona knowledge; não há gerador |
| G9 | **Template deletado após uso** | use_template() remove o .tmpl; correto para staging, mas não permite reutilizar |
| G10 | **load_project_context duplica analyze_project** | Lógica de stack em dois lugares; pode divergir |
| G11 | **Fastify sugere express-patterns** | Nome não bate; template é express-patterns.skill.tmpl |

### 6.3 Fluxo /init-engram

| # | Gap | Impacto |
|---|-----|---------|
| G12 | **Fase 3 não menciona DNA** | Conexão DNA → geração depende do Genesis SKILL |
| G13 | **Fase 4 "Popular Knowledge" é manual** | Claude preenche; não há script que extraia do código |
| G14 | **Templates removidos na Fase 7** | Se init-engram rodar em etapas, templates podem sumir antes de usar |
| G15 | **Sem validação pós-genesis** | Não verifica se conteúdo ainda tem TODO; GAPS G3.2 |

### 6.4 Referências e Integração

| # | Gap | Impacto |
|---|-----|---------|
| G16 | **compose.py pouco visível** | Não está no workflow do Genesis SKILL; só doctor/factory usam |
| G17 | **skill-patterns não cobre ORM/auth** | Padrões focam em workflow linear, decisão+ação; falta para prisma, auth |
| G18 | **Sem integração com analyze_project** | generate_component poderia receber sugestões (descrição, reason) |

### 6.5 Conhecimento

| # | Gap | Impacto |
|---|-----|---------|
| G19 | **Não gera knowledge** | knowledge.schema existe; Genesis não tem generate para isso |
| G20 | **Populate knowledge é 100% manual** | Nenhum script extrai PATTERNS do código ou DOMAIN de entidades |

---

## 7. Resumo: O Que Funciona

| Aspecto | Status |
|---------|--------|
| detect_stack | ✓ Robusto (10+ frameworks, ORMs, auth, etc.) |
| suggest_components skills | ✓ Framework + ORM + testes + auth + docker + devops |
| suggest_components agents | ✓ 3 universais + db-expert |
| Template matching (skills) | ✓ 11 frameworks com .skill.tmpl |
| generate_skill com template | ✓ Conteúdo rico (ex: nextjs-patterns) |
| generate_skill sem template | ✓ Scaffold genérico compatível com DNA |
| generate_agent | ✓ Scaffold válido |
| generate_command | ✓ Scaffold mínimo |
| validate | ✓ Cobre maioria das regras |
| register | ✓ Manifest atualizado |
| migrate_backup | ✓ Upgrade com preservação |
| compose | ✓ Resolução de composes |

---

## 8. Propostas de Melhoria (Priorizadas)

### Alta

| # | Ação | Esforço |
|---|------|---------|
| 1 | **G1: Sugerir commands** — deploy (se docker), migrate (se ORM), test (se testing) | Baixo |
| 2 | **G7: Enriquecer command scaffold** — padrões para status, plan, deploy a partir de --type | Médio |
| 3 | **G2: Agents por stack** — auth-expert (se auth), infra-expert (se k8s/terraform) | Médio |

### Média

| # | Ação | Esforço |
|---|------|---------|
| 4 | **G6: Agent com contexto** — tools e skills baseados em framework/orm do projeto | Médio |
| 5 | **G4: Filtrar já instalados** — analyze_project não sugerir nextjs-patterns se já existe | Baixo |
| 6 | **G10: Reusar detect_stack** — generate_component importar de analyze_project ou módulo compartilhado | Baixo |
| 7 | **G12: init-engram citar DNA** — Fase 3: "Consulte .claude/dna/[tipo].schema.md antes de gerar" | Trivial |

### Baixa

| # | Ação | Esforço |
|---|------|---------|
| 8 | **G3: Templates para ORM/auth** — prisma-workflow.skill.tmpl, auth-patterns.skill.tmpl | Alto |
| 9 | **G16: compose no Genesis SKILL** — Mencionar compose.py quando skill tiver composes | Trivial |
| 10 | **G15: Validação pós-genesis** — Script ou passo que verifica se há TODO excessivo | Médio |

---

## 9. Fluxo Simplificado

```
analyze_project → sugere o QUÊ criar (nomes)
       ↓
generate_component → cria o COMO (estrutura)
       ↓
Claude customiza → usa DNA + patterns
       ↓
validate → garante conformidade
       ↓
register → persiste no manifest
```

O Genesis depende de **Claude** para a customização. Os scripts fornecem scaffold e validação; o conteúdo real vem da interpretação do projeto pelo Claude.
