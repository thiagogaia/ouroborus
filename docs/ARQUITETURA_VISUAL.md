# Engram v4 — Arquitetura Visual e Partes Modificáveis

> Documento para visualizar o projeto, seus fundamentos e dividir em partes pequenas para modificação, validação e novas features.

---

## 0. Análise: A Divisão Core/Brain Faz Sentido?

**Resposta curta: SIM.** A divisão está alinhada com o código e com a separação de responsabilidades.

### Por que funciona

| Critério | Core | Brain |
|----------|------|-------|
| **Natureza** | Instruções (.md) + scripts de geração | Engine Python (storage + retrieval) |
| **Reutilização** | Universal (mesmo em qualquer projeto) | Engine universal; *dados* por projeto |
| **Dependência** | Core **usa** Brain (via recall, add_memory) | Brain **não depende** de Core |
| **Localização fonte** | `core/` | `.claude/brain/` (no repo) |
| **Instalação** | `setup.sh` copia para `.claude/` | `setup.sh` copia para `.claude/brain/` |

### Evidência no código

- **15+ commands** chamam `recall.py` ou `brain.add_memory()`
- **Todos os 3 agents** consultam o cérebro antes de propor decisões
- **7 skills** (knowledge-manager, domain-expert, code-reviewer, project-analyzer, etc.) registram ou consultam o cérebro
- **base-ingester** (Core seed) tem script Python que importa `brain_sqlite` — é ponte explícita Core→Brain

### Núcleo da separação

```
Core  = O QUE o Claude pode fazer (capacidades, workflows, orquestração)
Brain = ONDE o conhecimento vive (grafo, embeddings, recall)
```

Core define *como* usar; Brain *executa* o armazenamento e a busca.

### O que NÃO é domínio separado

- **knowledge/** — É interface/fallback. Genesis gera; populate lê no bootstrap; recall é a fonte primária. Não é terceiro domínio.
- **extras/** — Extensão do Core (skills/agents opcionais).
- **templates/** — Parte do Genesis (Core).
- **manifest.json** — Estado do ecossistema Core; Brain não o usa.

### Conclusão da análise

- **Manter** a divisão Core/Brain.
- **Não** criar domínios adicionais.
- **Única nuance:** `base-ingester` vive em Core mas importa Brain — é uma ponte intencional; faz sentido por ser um *seed* que alimenta o cérebro.

---

## 1. Visão Geral: Dois Domínios

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        ENGRAM v4 — Sistema Metacircular                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌──────────────────────────────┐     ┌──────────────────────────────────┐ │
│   │         CORE                  │     │          BRAIN                    │ │
│   │  (Melhoramento do Claude)     │     │  (Aprender sobre o projeto)       │ │
│   ├──────────────────────────────┤     ├──────────────────────────────────┤ │
│   │ • Gera skills, commands,     │     │ • Grafo de conhecimento           │ │
│   │   agents sob demanda         │◄────►│ • Busca semântica (embeddings)    │ │
│   │ • Evolui, aposenta, compõe   │     │ • Economia de tokens               │ │
│   │ • DNA (schemas)              │     │ • Assertividade em qualquer projeto│ │
│   └──────────────────────────────┘     └──────────────────────────────────┘ │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

| Domínio | Responsabilidade | Onde vive | Consumido por |
|---------|-------------------|-----------|---------------|
| **Core** | Capacidades do Claude (gerar, evoluir, orquestrar) | `core/` | Agents, skills, commands |
| **Brain** | Memória do projeto (aprender, buscar, consolidar) | `.claude/brain/` | Recall, Learn, Ingest |

---

## 2. Mapa da Árvore de Diretórios

```
ouroborusclaudegram_v2_final/
│
├── core/                          # ★ DOMÍNIO CORE (fonte)
│   ├── dna/                       # DNA — Schemas de validação
│   │   ├── agent.schema.md
│   │   ├── command.schema.md
│   │   ├── knowledge.schema.md
│   │   └── skill.schema.md
│   │
│   ├── genesis/                   # Motor de auto-geração
│   │   ├── SKILL.md
│   │   ├── scripts/
│   │   │   ├── analyze_project.py
│   │   │   ├── generate_component.py
│   │   │   ├── validate.py
│   │   │   ├── register.py
│   │   │   ├── compose.py
│   │   │   └── migrate_backup.py
│   │   └── references/
│   │
│   ├── evolution/                 # Motor de evolução
│   │   ├── SKILL.md
│   │   └── scripts/
│   │       ├── track_usage.py
│   │       ├── archive.py
│   │       ├── co_activation.py
│   │       ├── curriculum.py
│   │       ├── doctor.py
│   │       └── global_memory.py
│   │
│   ├── seeds/                     # Skills universais (templates)
│   │   ├── base-ingester/
│   │   ├── code-reviewer/
│   │   ├── domain-expert/
│   │   ├── engram-factory/
│   │   ├── knowledge-manager/
│   │   ├── priority-engine/
│   │   └── project-analyzer/
│   │
│   ├── agents/                    # Agents universais
│   │   ├── architect.md
│   │   ├── db-expert.md
│   │   └── domain-analyst.md
│   │
│   └── commands/                  # Commands universais
│       ├── init-engram.md
│       ├── learn.md
│       ├── recall.md
│       ├── create.md
│       ├── doctor.md
│       └── ... (16 total)
│
├── .claude/                       # ★ INSTALAÇÃO (projeto-alvo)
│   ├── brain/                     # DOMÍNIO BRAIN (runtime)
│   │   ├── brain_sqlite.py        # Núcleo do grafo
│   │   ├── recall.py              # Busca semântica
│   │   ├── sleep.py               # Consolidação (8 fases)
│   │   ├── cognitive.py           # Decay, archive, health
│   │   ├── populate.py            # Sync git → grafo
│   │   ├── embeddings.py          # Embeddings + ChromaDB
│   │   └── ...
│   │
│   ├── skills/                    # Skills instalados (core → aqui)
│   ├── agents/                    # Agents instalados
│   ├── commands/                  # Commands instalados
│   ├── knowledge/                 # .md fallback (PRIORITY_MATRIX editável)
│   ├── dna/                       # Schemas copiados
│   ├── manifest.json              # Estado do ecossistema
│   └── memory/                    # Memórias soltas (legado)
│
├── templates/                     # Templates para Genesis
│   ├── knowledge/
│   └── skills/                    # nextjs, react, django, etc.
│
├── setup.sh                       # Instalador (core + brain → .claude)
└── docs/
```

---

## 3. Fluxo de Dados: Core ↔ Brain

```
                    setup.sh
                        │
     ┌──────────────────┼──────────────────┐
     ▼                  ▼                  ▼
  core/dna       core/genesis       core/seeds
  core/evolution core/agents        core/commands
                        │
                        ▼
              .claude/ (skills, agents, commands)
                        │
                        │  /init-engram
                        ▼
  ┌─────────────────────────────────────────┐
  │  BRAIN                                   │
  │  populate.py → grafo (commits, ADRs,     │
  │  patterns, domain)                       │
  │  recall.py ← busca semântica             │
  │  sleep.py ← consolidação                 │
  └─────────────────────────────────────────┘
                        │
                        │  /learn
                        ▼
  brain.add_memory() → novas memórias
  sleep → relacionamentos semânticos
```

---

## 4. Partes Modificáveis (Incremental)

Cada bloco abaixo pode ser alterado, validado e entregue independentemente.

### 4.1 Brain — Partes Isoladas

| Bloco | Arquivos | Responsabilidade | Como validar |
|-------|----------|------------------|--------------|
| **B1. Grafo** | `brain_sqlite.py`, `brain.py` | Armazenamento, nós, arestas | `python brain_sqlite.py stats` |
| **B2. Embeddings** | `embeddings.py` | Gerar embeddings, ChromaDB/npz | `python embeddings.py build` |
| **B3. Recall** | `recall.py` | Busca semântica, spreading activation | `python recall.py "teste" --format json` |
| **B4. Sleep** | `sleep.py` | 8 fases de consolidação | `python sleep.py` |
| **B5. Cognitive** | `cognitive.py` | Decay, archive, health | `python cognitive.py health` |
| **B6. Populate** | `populate.py` | Git → grafo, refresh | `python populate.py refresh 20` |

**Testes:** `tests/brain/` cobre B1–B6.

### 4.2 Core — Partes Isoladas

| Bloco | Arquivos | Responsabilidade | Como validar |
|-------|----------|------------------|--------------|
| **C1. DNA** | `core/dna/*.schema.md` | Contratos de skills/agents/commands | Genesis valida contra eles |
| **C2. Genesis** | `core/genesis/scripts/*.py` | Gerar componentes | `validate.py`, `generate_component.py` |
| **C3. Evolution** | `core/evolution/scripts/*.py` | Rastrear uso, evoluir | `track_usage.py`, `doctor.py` |
| **C4. Seeds** | `core/seeds/*/SKILL.md` | Skills universais | Cursor usa SKILL.md |
| **C5. Agents** | `core/agents/*.md` | Especialistas | Claude invoca por nome |
| **C6. Commands** | `core/commands/*.md` | Fluxos (/learn, /recall, etc.) | Claude segue instruções |

### 4.3 Pontes Core–Brain

| Ponte | Onde | O que faz |
|-------|------|-----------|
| **/learn** | `core/commands/learn.md` | Usa `brain.add_memory()`, `populate.py`, `sleep.py` |
| **/recall** | `core/commands/recall.md` | Chama `recall.py` |
| **/init-engram** | `core/commands/init-engram.md` | Usa `populate.py`, `brain`, Genesis |
| **/doctor** | `core/commands/doctor.md` | Usa `cognitive.py health`, Evolution |
| **knowledge-manager** | `core/seeds/knowledge-manager/` | Orienta registro no cérebro |

---

## 5. Checklist para Novas Features

### Feature no Brain

1. **Escopo:** Qual bloco (B1–B6) ou novo script?
2. **Interface:** CLI (`argparse`) ou import Python?
3. **Teste:** Adicionar em `tests/brain/`.
4. **Integração:** Atualizar `learn.md` ou `recall.md` se necessário.

### Feature no Core

1. **Escopo:** DNA, Genesis, Evolution, Seed, Agent ou Command?
2. **Schema:** Se novo tipo, criar/atualizar `core/dna/*.schema.md`.
3. **Validação:** Usar `engram-genesis/scripts/validate.py`.
4. **Registro:** Usar `engram-genesis/scripts/register.py` se novo componente.

### Transversal (Core + Brain)

1. **Command novo:** `core/commands/nome.md` + uso de scripts em `brain/`.
2. **Skill que usa Brain:** Skill em `core/seeds/` ou gerado, referenciando `recall.py` ou `brain.add_memory()`.

---

## 6. Resumo Executivo

```
CORE = O que o Claude PODE FAZER (gerar, evoluir, orquestrar)
BRAIN = O que o Claude SABE (memória do projeto, assertividade)

Modificação incremental:
  Brain → testes em tests/brain/, scripts isolados
  Core  → schemas DNA, validate.py, manifest.json

Pontes: /learn, /recall, /init-engram, /doctor, knowledge-manager
```
