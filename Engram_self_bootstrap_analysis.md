# Engram — Análise de Mercado & Arquitetura Auto-Generativa

**Data:** 2026-02-03
**Contexto:** Pesquisa de soluções de mercado para sistemas auto-alimentados + proposta de arquitetura metacircular para o Engram.

---

## 1. Panorama de Mercado: Sistemas que se Auto-Geram

### 1.1 Voyager (NVIDIA/MineDojo) — O Padrão-Ouro

O Voyager é o projeto acadêmico mais influente nessa área. Um agente que joga Minecraft e **constrói sua própria biblioteca de skills** à medida que explora o mundo. Três componentes centrais:

| Componente | O que faz | Paralelo no Engram |
|---|---|---|
| **Automatic Curriculum** | Propõe tarefas baseado no nível atual de habilidade | Não existe — Engram é reativo |
| **Skill Library** | Armazena skills como código executável, indexado por embedding semântico | `.claude/skills/` — mas sem busca semântica |
| **Iterative Prompting + Self-Verification** | Gera código, testa, coleta feedback do ambiente, refina. Só comita na library se verificou sucesso | `/learn` registra, mas sem verificação |

**Insight-chave do Voyager:** Skills simples compõem skills complexas. "Minerar madeira" + "craftar tábuas" = "construir casa". Essa composicionalidade é o que faz o sistema escalar exponencialmente. O Engram **não tem composição de skills** — cada skill é uma ilha.

### 1.2 Darwin Gödel Machine (Sakana AI)

Um agente de código que **reescreve seu próprio código-fonte** para melhorar a si mesmo. Usa busca evolutiva aberta (não apenas hill-climbing): mantém um **arquivo de todas as versões históricas** e pode "ramificar" a partir de qualquer ancestral, não só do melhor atual.

**Insight-chave:** O DGM descobriu melhorias que eram transferíveis entre tarefas — não era overfitting. Engram poderia manter um "arquivo evolucionário" de versões de skills e medir quais variantes performam melhor.

### 1.3 BOSS (Bootstrap Your Own Skills)

Pesquisa da USC/Google que demonstra **bootstrapping bottom-up** de skills: o agente pratica encadear skills existentes, e quando descobre cadeias úteis, registra como nova skill. A biblioteca cresce ao longo do tempo tanto em quantidade quanto em horizonte temporal (skills que cobrem sequências mais longas).

**Insight-chave:** Skill creation não é "top-down" (humano decide) — é emergente da prática. O Engram poderia detectar padrões repetitivos no uso e propor novas skills automaticamente.

### 1.4 Ecossistema Claude Code Atual

| Projeto | Abordagem | Diferencial vs. Engram |
|---|---|---|
| **Claude Memory Bank** (hudrazine) | Docs hierárquicos inspirados no Cline | Workflow commands (`/understand`, `/plan`, `/execute`, `/update-memory`) |
| **Claude-Mem** (thedotmack) | Plugin com memória episódica comprimida + MCP tools | Busca semântica no histórico, subagente Haiku para compressão |
| **Self-Improving CLAUDE.md** (DEV.to) | Seção META que ensina Claude a escrever regras | O doc melhora a si mesmo quando erra |
| **Antigravity Awesome Skills** | 626+ skills portáveis entre Claude/Gemini/Codex | Open standard, instalação via npx |
| **Compound Engineering** (Every Inc) | 27 agents + 20 commands + 12 skills | "Gets smarter with every use" — learning loop |
| **Skill Creator** (Anthropic oficial) | Meta-skill que cria outras skills | `init_skill.py`, validação, packaging para `.skill` |
| **Local Skills Agent** | Sistema local (Ollama) onde o agente cria suas próprias skills | Skills como `.md`, auto-descoberta no startup |

### 1.5 Conceitos Acadêmicos Relevantes

| Conceito | Paper/Projeto | Aplicação no Engram |
|---|---|---|
| **Experience Replay para Prompting** | Self-Generated In-Context Examples (NeurIPS 2025) | Reusar interações passadas bem-sucedidas como exemplos |
| **Self-Challenging** | SCA - gera problemas e treina resolvendo-os | Engram poderia gerar "desafios de code review" para si mesmo |
| **SiriuS** | Multi-agent bootstrapped reasoning (NeurIPS 2025) | Biblioteca compartilhada de experiências entre agents |
| **SICA** | Agente que edita seu próprio scaffolding | O agent modifica seus próprios prompts/tools |
| **Compilador Metacircular** | Lisp, Jikes RVM, GNU Mes | Sistema definido em termos de si mesmo — aplicável ao Engram |

---

## 2. Gap Analysis: O que Falta no Engram

### O que o Engram faz bem
- Ciclo de retroalimentação explícito (`/learn` → knowledge → próxima sessão)
- Setup automatizado com detecção de stack
- Progressive disclosure (skills sob demanda)
- Knowledge files estruturados (state, patterns, priorities, decisions, domain)

### O que está faltando

| Gap | Severidade | Descrição |
|---|---|---|
| **Sem auto-geração de skills** | 🔴 ALTA | Skills são estáticos; o sistema não cria novos durante o uso |
| **Sem composição de skills** | 🔴 ALTA | Skills não podem invocar/compor outros skills |
| **Sem verificação/validação** | 🟡 MÉDIA | Nada testa se um skill funciona antes de registrá-lo |
| **Sem busca semântica** | 🟡 MÉDIA | Skills são ativados por trigger words, não por similaridade semântica |
| **Sem versionamento de skills** | 🟡 MÉDIA | Sem histórico de mudanças nos skills |
| **Sem métricas de uso** | 🟡 MÉDIA | Não sabe quais skills são úteis vs. desperdício |
| **Sem curriculum automático** | 🟢 BAIXA | Não sugere proativamente o que aprender |
| **Sem experience replay** | 🟢 BAIXA | Não reutiliza interações passadas como exemplos |
| **Sem skill pruning** | 🟢 BAIXA | Skills não são aposentados quando inúteis |

---

## 3. Arquitetura Proposta: Engram Metacircular

### 3.1 O Conceito: "O Sistema que se Gera"

A ideia é que o Engram contenha, como componente nuclear, a **capacidade de gerar a si mesmo**. Isso significa:

1. O Engram sabe qual é a estrutura de um skill, agent, command e knowledge file
2. O Engram pode analisar um projeto e decidir quais componentes precisa
3. O Engram pode gerar esses componentes usando suas próprias regras
4. O Engram pode validar e registrar os componentes gerados
5. O Engram pode evoluir os componentes existentes baseado em feedback

É o mesmo princípio de um **compilador que se compila** — o Engram instala uma versão mínima de si mesmo, que depois completa a instalação usando suas próprias capacidades.

### 3.2 Estrutura Proposta

```
engram/
├── core/                           # 🧬 DNA — o mínimo para o sistema existir
│   ├── schemas/                    # Schemas/templates de cada componente
│   │   ├── skill.schema.md         # O que define um skill válido
│   │   ├── agent.schema.md         # O que define um agent válido
│   │   ├── command.schema.md       # O que define um command válido
│   │   └── knowledge.schema.md     # O que define um knowledge file válido
│   │
│   ├── genesis/                    # O motor de auto-geração
│   │   ├── SKILL.md                # Meta-skill: "engram-genesis"
│   │   ├── scripts/
│   │   │   ├── analyze_project.py  # Analisa o projeto e detecta gaps
│   │   │   ├── generate_skill.py   # Gera um skill a partir do schema
│   │   │   ├── generate_agent.py   # Gera um agent a partir do schema
│   │   │   ├── validate.py         # Valida qualquer componente Engram
│   │   │   └── register.py         # Registra componente no sistema
│   │   └── references/
│   │       ├── skill-patterns.md   # Padrões comprovados de bons skills
│   │       └── anti-patterns.md    # O que NÃO fazer
│   │
│   ├── evolution/                  # Motor de evolução
│   │   ├── SKILL.md                # Meta-skill: "engram-evolution"
│   │   ├── scripts/
│   │   │   ├── track_usage.py      # Rastreia uso de cada componente
│   │   │   ├── measure_impact.py   # Mede impacto de cada skill (útil vs inútil)
│   │   │   ├── propose_merge.py    # Propõe fusão de skills relacionados
│   │   │   ├── propose_split.py    # Propõe split de skills muito grandes
│   │   │   └── archive.py          # Arquiva versões anteriores
│   │   └── references/
│   │       └── evolution-log.md    # Histórico de todas as evoluções
│   │
│   └── seeds/                      # Skills universais "semente"
│       ├── project-analyzer/       # Análise de codebase
│       ├── knowledge-manager/      # Retroalimentação
│       ├── domain-expert/          # Domínio de negócio
│       ├── priority-engine/        # ICE Score
│       └── code-reviewer/          # Code review
│
├── templates/                      # Templates iniciais (usados pelo genesis)
│   ├── skill-template/
│   │   └── SKILL.md.tmpl
│   ├── agent-template/
│   │   └── agent.md.tmpl
│   ├── command-template/
│   │   └── command.md.tmpl
│   └── knowledge-template/
│       ├── CURRENT_STATE.md.tmpl
│       ├── PATTERNS.md.tmpl
│       ├── PRIORITY_MATRIX.md.tmpl
│       ├── ADR_LOG.md.tmpl
│       └── DOMAIN.md.tmpl
│
├── extras/                         # Skills de nicho (não instalados por padrão)
│   ├── skills/
│   └── agents/
│
├── setup.sh                        # Instalador (Fase 0)
├── VERSION
├── LICENSE
└── README.md
```

### 3.3 As Quatro Fases da Auto-Geração

```
╔═══════════════════════════════════════════════════════════════════╗
║                    CICLO METACIRCULAR DO ENGRAM                  ║
╠═══════════════════════════════════════════════════════════════════╣
║                                                                   ║
║  FASE 0: BOOTSTRAP (setup.sh)                                    ║
║  ┌─────────────────────────────────────────────────────────┐      ║
║  │ • Detecta stack do projeto                              │      ║
║  │ • Instala core/schemas + core/genesis + core/seeds      │      ║
║  │ • Gera CLAUDE.md e knowledge templates                  │      ║
║  │ • NÃO gera skills específicos do projeto                │      ║
║  └──────────────────────────────┬──────────────────────────┘      ║
║                                 ▼                                  ║
║  FASE 1: GÊNESE (/init-engram usando genesis skill)               ║
║  ┌─────────────────────────────────────────────────────────┐      ║
║  │ • Claude analisa o projeto em profundidade               │      ║
║  │ • genesis detecta quais skills o projeto PRECISA         │      ║
║  │ • Para cada necessidade:                                 │      ║
║  │   1. Consulta schemas/ para entender a estrutura         │      ║
║  │   2. Consulta skill-patterns.md para boas práticas       │      ║
║  │   3. Gera o skill usando generate_skill.py               │      ║
║  │   4. Valida com validate.py                              │      ║
║  │   5. Registra com register.py                            │      ║
║  │ • Popula knowledge files com estado real                 │      ║
║  └──────────────────────────────┬──────────────────────────┘      ║
║                                 ▼                                  ║
║  FASE 2: USO + AUTO-EVOLUÇÃO (durante trabalho normal)            ║
║  ┌─────────────────────────────────────────────────────────┐      ║
║  │ • Claude trabalha normalmente com skills existentes      │      ║
║  │ • evolution/track_usage.py registra cada ativação        │      ║
║  │ • Quando Claude detecta padrão repetitivo sem skill:     │      ║
║  │   → Propõe criação via genesis                           │      ║
║  │ • Quando Claude detecta skill ineficiente:               │      ║
║  │   → Propõe evolução via evolution                        │      ║
║  └──────────────────────────────┬──────────────────────────┘      ║
║                                 ▼                                  ║
║  FASE 3: REFLEXÃO (/learn com evolution skill)                    ║
║  ┌─────────────────────────────────────────────────────────┐      ║
║  │ • Analisa commits + introspecção (já existe)             │      ║
║  │ + NOVO: Revisa métricas de uso dos skills                │      ║
║  │ + NOVO: Identifica skills subutilizados → archive        │      ║
║  │ + NOVO: Identifica oportunidades de composição           │      ║
║  │ + NOVO: Propõe novas skills para padrões recorrentes     │      ║
║  │ + NOVO: Versiona skills modificados                      │      ║
║  └──────────────────────────────┬──────────────────────────┘      ║
║                                 │                                  ║
║                                 ▼                                  ║
║                    🐍 Ciclo se repete (Ouroboros)                  ║
╚═══════════════════════════════════════════════════════════════════╝
```

### 3.4 O Schema: O "DNA" do Sistema

O coração da auto-geração é o **schema** — a definição formal de cada componente. O genesis usa os schemas para gerar componentes que são estruturalmente corretos por construção.

#### `core/schemas/skill.schema.md`

```markdown
# Skill Schema v1.0

## Estrutura de Diretório
skill-name/
├── SKILL.md          (obrigatório)
├── scripts/          (opcional — código executável)
├── references/       (opcional — docs para contexto)
└── assets/           (opcional — templates, arquivos de output)

## SKILL.md — Frontmatter (YAML)
Campos obrigatórios:
- name: string — identificador único, kebab-case
- description: string — O QUE faz + QUANDO ativar (triggers)

## SKILL.md — Body (Markdown)
Seções recomendadas:
- Contexto/Propósito (1-2 parágrafos)
- Workflow (steps numerados)
- Regras/Guardrails
- Output Esperado

## Regras de Validação
1. SKILL.md deve existir e ter frontmatter válido
2. name deve ser kebab-case e único no projeto
3. description deve ter >50 e <500 caracteres
4. Body deve ter <500 linhas (progressive disclosure)
5. Referências a scripts/ devem apontar para arquivos existentes
6. Scripts devem ser executáveis e ter shebang line
```

#### `core/schemas/agent.schema.md`

```markdown
# Agent Schema v1.0

## Estrutura
agent-name.md (arquivo único no diretório agents/)

## Frontmatter (YAML)
Campos obrigatórios:
- name: string — identificador
- description: string — especialidade + quando invocar
- tools: lista de permissões (Read, Write, Bash, etc.)
Campos opcionais:
- skills: lista de skills que o agent usa

## Body (Markdown)
- Identidade (quem é o agent)
- Responsabilidades (o que faz)
- Princípios (como decide)
- Regras (limites)
- Output Esperado (formato de resposta)

## Regras de Validação
1. Agent NÃO pode invocar outros agents (design rule)
2. Tools devem ser subset das permissões do settings.json
3. Skills referenciados devem existir em .claude/skills/
```

### 3.5 O Genesis Skill — Detalhamento

Este é o componente mais importante da arquitetura: o skill que gera outros skills.

```markdown
---
name: engram-genesis
description: Motor de auto-geração do Engram. Use quando precisar criar
  um novo skill, agent, command ou knowledge file. Também ativado pelo
  /init-engram para gerar a instalação completa do projeto. Capacidade
  metacircular — este skill pode gerar versões atualizadas de si mesmo.
---

# Engram Genesis

## Propósito
Gerar componentes Engram (skills, agents, commands, knowledge files)
que são estruturalmente corretos e adaptados ao projeto atual.

## Workflow de Geração

### 1. Análise de Necessidade
- Identificar qual componente é necessário
- Analisar o contexto do projeto (stack, patterns, domain)
- Verificar se já existe componente similar (evitar duplicação)

### 2. Consultar Schema
- Ler o schema correspondente em core/schemas/
- Entender estrutura obrigatória e regras de validação

### 3. Consultar Padrões
- Ler references/skill-patterns.md para boas práticas
- Ler references/anti-patterns.md para evitar erros comuns
- Analisar skills existentes como exemplos

### 4. Gerar Componente
- Usar scripts/generate_skill.py (ou equivalente)
- Preencher template com dados do projeto
- Customizar para a stack detectada

### 5. Validar
- Executar scripts/validate.py no componente gerado
- Verificar estrutura, frontmatter, referências
- Se falhar: corrigir e re-validar

### 6. Registrar
- Copiar para o diretório correto (.claude/skills/, agents/, etc.)
- Atualizar CLAUDE.md se necessário
- Registrar em knowledge/context/CURRENT_STATE.md

## Capacidade Metacircular
Este skill pode gerar uma versão atualizada de si mesmo.
Para isso:
1. Analisa a versão atual
2. Identifica melhorias baseado no uso
3. Gera nova versão seguindo seu próprio schema
4. Valida e substitui (mantendo backup)
```

### 3.6 O Evolution Skill — Detalhamento

```markdown
---
name: engram-evolution
description: Motor de evolução do Engram. Rastreia uso de componentes,
  mede impacto, propõe melhorias, fusões e aposentadorias. Use no /learn
  para análise evolutiva, ou quando Claude detectar skill ineficiente.
---

# Engram Evolution

## Métricas Rastreadas
Para cada componente:
- **Frequência**: quantas vezes foi ativado
- **Contexto**: em quais tipos de tarefa
- **Duração**: quanto da sessão foi gasto no skill
- **Outcome**: tarefa completada com sucesso?
- **Feedback**: dev fez thumbs up/down? Pediu mudança?

## Ações Evolutivas

### Propor Novo Skill
Quando: padrão repetitivo detectado (>3 vezes mesma sequência sem skill)
Como: coletar exemplos → abstrair padrão → invocar genesis

### Evoluir Skill Existente
Quando: skill ativado mas frequentemente complementado com instruções adicionais
Como: analisar instruções extras → incorporar no SKILL.md

### Compor Skills
Quando: dois skills sempre ativados em sequência
Como: criar skill composto que orquestra ambos

### Dividir Skill
Quando: skill muito grande (>500 linhas) ou com múltiplas responsabilidades
Como: identificar responsabilidades → gerar skills especializados

### Aposentar Skill
Quando: skill não ativado em >10 sessões
Como: mover para .claude/archive/ com nota explicativa

### Versionar Skill
Quando: skill modificado
Como: copiar versão anterior para .claude/versions/skill-name/v{N}.md
```

---

## 4. Novas Features Propostas (Baseado em Mercado)

### 4.1 Prioridade ALTA — Diferenciais Competitivos

#### Feature: Skill Composition Engine
**Inspiração:** Voyager (composição de skills simples → complexos)
**O que é:** Skills podem declarar dependências de outros skills e orquestrar sub-workflows.

```yaml
# Em um SKILL.md
---
name: full-feature-pipeline
description: Pipeline completo para implementar uma feature
composes:
  - project-analyzer    # Fase 1: entender o projeto
  - priority-engine     # Fase 2: validar prioridade
  - code-reviewer       # Fase 3: revisar resultado
---
```

**Impacto:** Skills compostos permitem automação de workflows complexos sem duplicação.

#### Feature: Auto-Detect & Propose Skills
**Inspiração:** BOSS (skill bootstrapping bottom-up)
**O que é:** Durante o trabalho, quando Claude executa sequências repetitivas que não correspondem a nenhum skill, ele propõe a criação de um novo skill.

```
[Claude detecta que nas últimas 3 sessões, o dev sempre:
 1. Lê o schema Prisma
 2. Gera um Zod schema correspondente
 3. Cria um Server Action com validação]

Claude: "Notei que você repete um padrão de Prisma→Zod→ServerAction.
Quer que eu crie um skill 'prisma-to-action' para automatizar isso?"
```

**Impacto:** O sistema evolui organicamente baseado no uso real, não em suposições.

#### Feature: Skill Manifest com Métricas
**Inspiração:** Evolution log + Voyager skill library
**O que é:** Um arquivo `.claude/manifest.json` que rastreia todos os componentes, versões, uso e saúde.

```json
{
  "version": "1.0.0",
  "installed": "2026-02-03",
  "components": {
    "skills": {
      "project-analyzer": {
        "version": "1.0.0",
        "source": "core/seeds",
        "activations": 47,
        "last_used": "2026-02-03",
        "health": "active"
      },
      "prisma-to-action": {
        "version": "1.0.0",
        "source": "genesis/auto-generated",
        "activations": 12,
        "last_used": "2026-02-02",
        "health": "active",
        "generated_from": "pattern-detection-session-42"
      }
    }
  }
}
```

### 4.2 Prioridade MÉDIA — Polish que Importa

#### Feature: Experience Library
**Inspiração:** SiriuS, Self-Generated In-Context Examples
**O que é:** Interações bem-sucedidas são comprimidas e armazenadas como exemplos reutilizáveis. Quando Claude enfrenta uma tarefa similar, busca exemplos relevantes na library.

Novo knowledge file: `.claude/knowledge/experiences/EXPERIENCE_LIBRARY.md`

```markdown
## EXP-001: Migração de API Route para Server Action
- **Contexto**: Migrar endpoint POST /api/users para Server Action
- **Stack**: Next.js 14 + Prisma + Zod
- **Padrão aplicado**: form-action-pattern (PATTERNS.md #3)
- **Resultado**: Sucesso, reduziu 40% das linhas
- **Sessão**: 2026-01-28
```

#### Feature: `/doctor` Command
**Inspiração:** Health checks em ferramentas de dev (npm doctor, brew doctor)
**O que é:** Diagnostica a saúde do Engram no projeto.

```bash
/doctor

🐍 Engram Health Check
═══════════════════════
✅ CLAUDE.md presente e válido
✅ settings.json válido
✅ 7 skills instalados, 7 válidos
⚠️  knowledge-manager: última atualização há 5 dias
⚠️  PRIORITY_MATRIX.md: 3 itens sem atualização em 2 semanas
❌ db-expert agent referencia skill "prisma-optimizer" que não existe
✅ Manifest atualizado
Saúde geral: 🟡 85%
```

#### Feature: Skill Templates por Stack
**Inspiração:** `setup.sh` já detecta stack — estender para gerar skills específicos
**O que é:** Biblioteca de templates de skills pré-configurados por stack.

```
templates/
├── stacks/
│   ├── nextjs/
│   │   ├── server-actions.skill.tmpl
│   │   ├── app-router.skill.tmpl
│   │   └── metadata-seo.skill.tmpl
│   ├── django/
│   │   ├── views-patterns.skill.tmpl
│   │   └── migrations.skill.tmpl
│   ├── fastapi/
│   │   ├── pydantic-models.skill.tmpl
│   │   └── dependency-injection.skill.tmpl
│   └── laravel/
│       ├── eloquent-patterns.skill.tmpl
│       └── blade-components.skill.tmpl
```

O genesis usa esses templates como ponto de partida, mas customiza para o projeto específico.

### 4.3 Prioridade BAIXA — Roadmap Futuro

#### Feature: Skill Marketplace
Permitir que devs compartilhem skills gerados. Um `engram publish` que envia para um registry.

#### Feature: Multi-Project Memory
Um Engram "global" (`~/.engram/`) que carrega aprendizados entre projetos. "Você resolveu um problema similar no projeto X com o padrão Y."

#### Feature: Automatic Curriculum
Inspirado no Voyager. O Engram sugere proativamente: "Baseado no seu projeto, você deveria aprender sobre: rate limiting (sua API não tem), error boundaries (faltam em 3 rotas), e18n (seu projeto tem strings hardcoded em pt-BR)."

---

## 5. Estrutura Concreta para Auto-Geração

### 5.1 O Mínimo Viável: `setup.sh` v2

O setup.sh atual já é bom. A mudança principal é: **não instalar skills específicos do projeto**. Em vez disso, instalar o `genesis` e deixar o `/init-engram` gerar o que precisa.

```bash
# setup.sh v2 — o que muda:

# ANTES: copia skills fixos
# cp -r "$SCRIPT_DIR/.claude" "$TARGET_DIR/.claude"

# DEPOIS: copia apenas o core
copy_core() {
    # 1. Schemas (DNA do sistema)
    cp -r "$SCRIPT_DIR/core/schemas" "$TARGET_DIR/.claude/schemas/"
    
    # 2. Genesis skill (motor de geração)
    cp -r "$SCRIPT_DIR/core/genesis" "$TARGET_DIR/.claude/skills/engram-genesis/"
    
    # 3. Evolution skill (motor de evolução)
    cp -r "$SCRIPT_DIR/core/evolution" "$TARGET_DIR/.claude/skills/engram-evolution/"
    
    # 4. Seeds (skills universais mínimos)
    cp -r "$SCRIPT_DIR/core/seeds/"* "$TARGET_DIR/.claude/skills/"
    
    # 5. Templates de knowledge
    cp -r "$SCRIPT_DIR/templates/knowledge/"* "$TARGET_DIR/.claude/knowledge/"
    
    # 6. Commands essenciais
    cp -r "$SCRIPT_DIR/core/commands/"* "$TARGET_DIR/.claude/commands/"
    
    # 7. Manifest vazio
    echo '{"version":"1.0.0","components":{}}' > "$TARGET_DIR/.claude/manifest.json"
}

# O /init-engram agora é MUITO mais poderoso:
# Usa genesis para gerar skills específicos para o projeto
# Usa os schemas para garantir que tudo é válido
# Registra tudo no manifest
```

### 5.2 O `/init-engram` v2

```markdown
# /init-engram v2

## Fase 1: Análise Profunda
1. Analisar o codebase (estrutura, dependências, padrões existentes)
2. Ler qualquer CLAUDE.md.bak ou .claude.bak (migração)
3. Identificar domínio de negócio
4. Mapear workflows do dev (scripts no package.json, CI/CD)

## Fase 2: Auto-Geração via Genesis
Para cada necessidade detectada:
1. Ativar skill engram-genesis
2. Consultar schema correspondente
3. Gerar componente customizado para ESTE projeto
4. Validar com validate.py
5. Registrar no manifest.json

### Decisões de geração:
- Stack é Next.js? → gerar skill "nextjs-patterns"
- Tem Prisma? → gerar agent "db-expert" customizado para o schema real
- Tem testes? → gerar skill "test-patterns" para o framework detectado
- Tem Docker? → gerar skill "docker-workflow"
- Tem N8N? → gerar skills de extras/ relevantes

## Fase 3: Popular Knowledge
- CURRENT_STATE.md com análise real
- PATTERNS.md com padrões detectados no código existente
- DOMAIN.md com glossário extraído do código/docs
- PRIORITY_MATRIX.md com TODOs e issues detectados

## Fase 4: Validação
- /doctor automático
- Relatório do que foi gerado e por quê
```

### 5.3 O Ciclo de Auto-Melhoria em Ação

```
Sessão 1 (instalação):
  $ ./setup.sh /meu-projeto
  $ claude
  $ /init-engram
  → Genesis cria: nextjs-patterns, prisma-workflow, zod-validation
  → 3 agents gerados: architect, db-expert (Prisma), api-designer
  → Knowledge populado

Sessão 2 (trabalho normal):
  Dev: "Preciso criar um CRUD de produtos"
  → Claude ativa: nextjs-patterns + prisma-workflow + zod-validation
  → Trabalha normalmente
  → No /learn: evolution registra que os 3 skills foram usados juntos

Sessão 3 (trabalho normal):
  Dev: "Agora um CRUD de categorias"
  → Mesmo padrão de ativação
  → No /learn: evolution detecta padrão recorrente

Sessão 4 (evolução):
  → Evolution propõe: "Criar skill composto 'crud-pipeline'
     que orquestra nextjs-patterns → prisma-workflow → zod-validation?"
  Dev: "Sim!"
  → Genesis cria 'crud-pipeline' usando schemas + padrões dos 3 skills
  → Valida e registra

Sessão 5+:
  Dev: "CRUD de pedidos"
  → Claude ativa crud-pipeline (1 skill em vez de 3)
  → Mais eficiente, menos contexto consumido
```

---

## 6. Comparação: Antes vs. Depois

| Aspecto | Engram Atual | Engram Metacircular |
|---|---|---|
| Instalação | Copia skills fixos | Instala DNA + genesis, gera sob demanda |
| Skills | 5 universais + extras manuais | 5 seeds + N auto-gerados por projeto |
| Evolução | Manual (dev edita skills) | Automática (evolution propõe, genesis executa) |
| Composição | Impossível | Skills podem orquestrar sub-skills |
| Validação | Nenhuma | Schema-driven, validate.py |
| Métricas | Nenhuma | Manifest com uso, saúde, versões |
| Adaptação | Setup detecta stack | Genesis gera skills customizados para stack |
| Pruning | Nenhum | Evolution aposenta skills inativos |
| Versionamento | Nenhum | Archive automático de versões |
| Portabilidade | Só Claude Code | Schemas são agent-agnostic |

---

## 7. Roadmap de Implementação

### Sprint 1: Foundation (v1.0 → v1.5)
1. Criar `core/schemas/` com schemas de skill, agent, command
2. Criar `core/genesis/` com SKILL.md + scripts básicos
3. Criar `manifest.json` e script de tracking
4. Refatorar `setup.sh` para instalar core + seeds
5. Atualizar `/init-engram` para usar genesis

### Sprint 2: Evolution (v1.5 → v2.0)
6. Criar `core/evolution/` com SKILL.md + scripts
7. Implementar tracking de uso no `/learn`
8. Implementar proposta de novos skills (pattern detection)
9. Implementar versionamento de skills
10. Implementar `/doctor`

### Sprint 3: Composition (v2.0 → v2.5)
11. Adicionar campo `composes:` ao skill schema
12. Implementar orquestração de sub-skills
13. Implementar skill templates por stack
14. Implementar experience library

### Sprint 4: Ecosystem (v2.5 → v3.0)
15. Compatibilidade com Agent Skill Standard (open standard)
16. `engram publish` para compartilhar skills
17. Multi-project memory
18. Automatic curriculum

---

## 8. Resumo Executivo

O Engram já tem uma base sólida. O ciclo de retroalimentação, a detecção de stack, e o progressive disclosure são diferenciais reais. O que falta é transformá-lo de um **sistema estático que instala componentes fixos** em um **sistema vivo que gera seus próprios componentes**.

A inspiração principal vem de três fontes:

1. **Voyager** → Skill library composicional que cresce por uso
2. **Darwin Gödel Machine** → Sistema que modifica a si mesmo e mantém arquivo evolutivo
3. **Compilador Metacircular** → O sistema é definido em termos de si mesmo

A mudança arquitetural central é separar o **DNA** (schemas/templates) do **organismo** (skills/agents gerados). O `setup.sh` instala o DNA. O `/init-engram` + uso diário faz o organismo crescer. O `/learn` faz o organismo evoluir.

O Engram deixa de ser um "kit de instalação" e se torna um **sistema vivo de memória e evolução para Claude Code**.