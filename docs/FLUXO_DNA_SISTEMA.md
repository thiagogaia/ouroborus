# Fluxo do DNA no Sistema Engram

> Como o DNA (schemas) flui através de init-engram, create, Genesis e Evolution.

---

## 1. Papel do DNA

O DNA define **o que é válido** para:
- **Skills** — estrutura, frontmatter, body
- **Agents** — estrutura, frontmatter, body
- **Commands** — estrutura, body (sem frontmatter)
- **Knowledge** — estrutura de pastas, formato de cada arquivo

O DNA **não gera** nada sozinho. Ele é a **referência** que o Genesis usa ao criar.

---

## 2. Fluxo Visual

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  setup.sh                                                                    │
│  Copia core/dna/ → .claude/dna/                                              │
│  Cria estrutura knowledge/ (templates)                                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                         │
                                         │ DNA instalado no projeto
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  .claude/dna/                                                                │
│  ├── skill.schema.md                                                         │
│  ├── agent.schema.md                                                         │
│  ├── command.schema.md                                                       │
│  └── knowledge.schema.md                                                    │
└─────────────────────────────────────────────────────────────────────────────┘
                    │                    │                    │
                    │                    │                    │
        ┌───────────┴───────────┐        │        ┌───────────┴───────────┐
        │  /init-engram         │        │        │  /create [tipo] [nome]  │
        │  (start do projeto)   │        │        │  (sob demanda)          │
        └───────────┬───────────┘        │        └───────────┬───────────┘
                    │                    │                    │
                    │ "Ativar Genesis"  │                    │ "Ativar Genesis"
                    │ Fase 3             │                    │
                    ▼                    │                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  engram-genesis (SKILL)                                                      │
│                                                                              │
│  Workflow:                                                                   │
│    1. Entender necessidade                                                  │
│    2. ★ CONSULTAR SCHEMA em .claude/dna/ ★                                  │
│       - skill.schema.md para skills                                          │
│       - agent.schema.md para agents                                          │
│       - command.schema.md para commands                                      │
│       - knowledge.schema.md para knowledge                                   │
│    3. Consultar skill-patterns, anti-patterns                               │
│    4. generate_component.py (scaffold)                                       │
│    5. Customizar (Claude usa o schema como guia)                             │
│    6. validate.py (checa contra regras do schema)                            │
│    7. register.py                                                            │
└─────────────────────────────────────────────────────────────────────────────┘
                    │                    │                    │
                    │                    │                    │
                    │                    │                    │
        ┌───────────┴───────────┐        │        ┌───────────┴───────────┐
        │  /learn              │        │        │  knowledge-manager    │
        │  Fase 5: Evolution   │        │        │  (skill)               │
        └───────────┬───────────┘        │        └───────────┬───────────┘
                    │                    │                    │
                    │ "Propor novo       │                    │ Referencia
                    │  skill/agent"     │                    │ knowledge.schema
                    │                    │                    │ para PRIORITY_MATRIX
                    ▼                    │                    │
┌─────────────────────────────────────────────────────────────────────────────┐
│  engram-evolution (SKILL)                                                    │
│                                                                              │
│  Detecta: padrão recorrente, skill grande, co-ativação...                   │
│  Proposta: "Criar skill X?"                                                   │
│  Se aprovado → invoca engram-genesis                                          │
│                    │                                                          │
│                    └───────────────────────────────► Genesis usa DNA        │
│                                                                              │
│  Evolution NÃO lê DNA diretamente.                                           │
│  Mas quando propõe composes:, deveria saber que skill.schema tem composes:   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Detalhamento por Ponto de Entrada

### 3.1 /init-engram — Start do Projeto

| Fase | Usa DNA? | Como |
|------|----------|------|
| 0. Migração | Não | migrate_backup |
| 1. Análise | Não | analyze_project sugere *nomes* (não estrutura) |
| 2. Plano | Não | Apresenta lista ao dev |
| **3. Auto-Geração** | **Sim, via Genesis** | "Ativar skill engram-genesis" → Genesis segue seu workflow incluindo "Consultar Schema" |
| 4. Popular Knowledge | Implícito | Formato de PATTERNS, DOMAIN, etc. segue knowledge.schema |
| 5. Popular Cérebro | Não | populate.py |
| 6. Doctor | Parcial | Doctor verifica que .claude/dna existe |

O init-engram **não menciona DNA** explicitamente. A ligação é: init-engram delega a geração para o Genesis, e o Genesis instrui a consultar o DNA.

### 3.2 /create [tipo] [nome] — Sob Demanda

| Passo | Usa DNA? | Como |
|-------|----------|------|
| 1. Validar nome | Não | kebab-case |
| 2. Ativar Genesis | Sim | Genesis diz "Consultar schema correspondente" |
| 3. Gerar | Sim | generate_component + customização guiada pelo schema |
| 4. Validar | Sim | validate.py aplica regras do schema |
| 5. Registrar | Não | register.py |

O create **instrui** a consultar o schema; o Genesis é quem de fato usa o DNA.

### 3.3 /learn — Evolução

| Fase | Usa DNA? | Como |
|------|----------|------|
| 1–4. Cérebro | Não | brain.add_memory, sleep |
| **5. Evolution** | **Indiretamente** | Evolution propõe novo skill → se aprovado → Genesis cria → Genesis usa DNA |

O Evolution não lê o DNA. Ele propõe "criar skill X" ou "skill composto com composes: [a,b]". Quando o dev aprova, **Genesis** é invocado e aí o DNA entra.

### 3.4 knowledge-manager (skill)

Referencia explicitamente `.claude/dna/knowledge.schema.md` para manter o formato do PRIORITY_MATRIX.

---

## 4. Resumo: Quem Usa o DNA e Como

| Componente | Usa DNA? | Forma |
|------------|----------|-------|
| **setup.sh** | Instala | Copia core/dna → .claude/dna |
| **init-engram** | Indiretamente | Fase 3 delega ao Genesis → Genesis consulta DNA |
| **create** | Indiretamente | Delega ao Genesis → Genesis consulta DNA |
| **Genesis (SKILL)** | Diretamente | Passo 2: "Consultar Schema em .claude/dna/" |
| **Genesis (scripts)** | Parcialmente | validate.py implementa regras; generate_component não lê schema |
| **Evolution** | Indiretamente | Proposta aprovada → Genesis cria → Genesis usa DNA |
| **knowledge-manager** | Diretamente | Referencia knowledge.schema para PRIORITY_MATRIX |
| **doctor** | Estrutural | Verifica que .claude/dna existe |

---

## 5. Lacuna Atual

O **init-engram** não diz explicitamente "consulte o DNA" ou "siga os schemas". A conexão é:

```
init-engram Fase 3: "Ativar skill engram-genesis. Para cada componente..."
    → Genesis SKILL: "Consultar Schema em .claude/dna/"
```

Ou seja: quem executa o init-engram (Claude) precisa **ativar o Genesis** e o Genesis é que traz a instrução de consultar o DNA. Se alguém pular o Genesis e gerar manualmente, o DNA pode ser ignorado.

**Sugestão:** Na Fase 3 do init-engram, acrescentar explicitamente:

> "Antes de gerar cada componente, consulte o schema em `.claude/dna/[tipo].schema.md` para garantir estrutura correta."

Isso torna o fluxo DNA → init-engram mais explícito.

---

## 6. Fluxo Simplificado

```
DNA = contrato (o que é válido)
       ↓
Genesis = motor que cria (lê o contrato)
       ↓
init-engram / create = quando criar (invocam Genesis)
Evolution = quando evoluir (propõe → Genesis cria)
```

O DNA é o **fio condutor** da criação. Tudo que é skill, agent, command ou knowledge novo passa pelo Genesis, e o Genesis usa o DNA como referência.
