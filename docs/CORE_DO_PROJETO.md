# Core do Projeto Engram — O Que É e O Que Não É

> Documento que define o núcleo do Engram, separando o que é essencial (metacircular) do que é feature adicional (cérebro).

---

## Resumo Executivo

| Camada | O que é | Origem |
|--------|---------|--------|
| **Core** | Metacircular: DNA + Genesis + Evolution + Seeds + Agents + Commands | v1/v2 |
| **Brain** | Memória organizacional: grafo + embeddings + recall + sleep | v3 (adicional) |

O **core** funciona sem o cérebro: skills, agents e commands podem operar com arquivos `.md` em `knowledge/`. O cérebro é uma **feature de memória avançada** que surgiu depois e se tornou central no workflow v4, mas não é o cerne metacircular.

---

## 1. O Que É o Core

O core é o **sistema metacircular** — a capacidade de o Engram gerar e evoluir a si mesmo. Representa **o que o Claude pode fazer**, não onde o conhecimento vive.

### 1.1 Estrutura em `core/`

```
core/
├── dna/                    # Contratos formais
│   ├── skill.schema.md
│   ├── agent.schema.md
│   ├── command.schema.md
│   └── knowledge.schema.md
│
├── genesis/                # Motor de auto-geração
│   ├── SKILL.md
│   └── scripts/
│       ├── analyze_project.py
│       ├── generate_component.py
│       ├── validate.py
│       ├── register.py
│       ├── compose.py
│       └── migrate_backup.py
│
├── evolution/              # Motor de evolução
│   ├── SKILL.md
│   └── scripts/
│       ├── track_usage.py
│       ├── archive.py
│       ├── co_activation.py
│       ├── curriculum.py
│       ├── doctor.py
│       └── global_memory.py
│
├── seeds/                  # Skills universais
│   ├── base-ingester/
│   ├── code-reviewer/
│   ├── domain-expert/
│   ├── engram-factory/
│   ├── knowledge-manager/
│   ├── priority-engine/
│   └── project-analyzer/
│
├── agents/                 # Especialistas universais
│   ├── architect.md
│   ├── db-expert.md
│   └── domain-analyst.md
│
└── commands/               # Slash commands (15)
    ├── init-engram.md
    ├── learn.md
    ├── create.md
    ├── doctor.md
    ├── recall.md
    └── ...
```

### 1.2 Componentes do Core

| Componente | Responsabilidade | Independente do Brain? |
|------------|------------------|------------------------|
| **DNA** | Schemas de validação (skill, agent, command, knowledge) | ✅ Sim |
| **Genesis** | Analisar projeto, gerar skills/agents, validar contra DNA | ✅ Sim (escreve em .md) |
| **Evolution** | Rastrear uso, propor arquivamento, composição, versões | ✅ Sim (manifest.json) |
| **Seeds** | Skills universais (project-analyzer, code-reviewer, etc.) | ⚠️ Parcial (knowledge-manager pode usar .md) |
| **Agents** | Especialistas (architect, db-expert, domain-analyst) | ⚠️ Parcial (podem consultar recall) |
| **Commands** | Fluxos (/init-engram, /learn, /create, /doctor, etc.) | ⚠️ Parcial (/learn, /recall chamam brain) |

---

## 2. O Que NÃO É Core (Features Adicionais)

### 2.1 Brain (`.claude/brain/`)

O cérebro organizacional é uma **feature de memória avançada** adicionada em v3:

- **Storage**: SQLite (grafo) + ChromaDB (embeddings)
- ** retrieval**: recall.py (busca semântica + spreading activation)
- **Consolidação**: sleep.py (8 fases)
- **Manutenção**: cognitive.py (decay, archive, health)

**Função**: Oferecer busca semântica, economia de tokens e assertividade no conhecimento do projeto. O core **usa** o brain via recall/add_memory, mas o core **não depende** dele para existir — os arquivos `.md` em `knowledge/` são o fallback.

### 2.2 Extras (`extras/`)

Skills e agents opcionais para nichos específicos (n8n, fintech, devops). Nunca instalados automaticamente.

### 2.3 Templates (`templates/`)

Scaffolding para Genesis. São **parte do Genesis** ( Core), mas representam conteúdo de apoio, não a lógica metacircular.

---

## 3. Hierarquia Conceitual

```
┌─────────────────────────────────────────────────────────────────┐
│  CORE (Metacircular)                                             │
│  ─────────────────                                               │
│  • DNA: contratos                                                │
│  • Genesis: gera componentes sob demanda                         │
│  • Evolution: evoluir, aposentar, compor                         │
│  • Seeds: skills universais                                      │
│  • Agents: especialistas                                         │
│  • Commands: fluxos de trabalho                                  │
│                                                                  │
│  Regra: "Se é útil em QUALQUER projeto, vai no core"             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ usa (quando disponível)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  BRAIN (Feature de Memória)                                      │
│  ──────────────────────────                                      │
│  • Grafo de conhecimento                                         │
│  • Busca semântica                                               │
│  • Consolidação (sleep)                                          │
│                                                                  │
│  Regra: "ONDE o conhecimento vive"                                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ fallback
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  KNOWLEDGE (.md)                                                  │
│  ───────────────                                                 │
│  • CURRENT_STATE.md, ADR_LOG.md, PATTERNS.md, etc.               │
│  • Genesis gera; recall é fonte primária quando brain existe     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. Evolução Histórica

| Versão | Foco | Core vs Brain |
|-------|------|---------------|
| **v1** | Fixed — skills estáticos, evolução manual | Só core (sem genesis/evolution) |
| **v2** | Metacircular — genesis + evolution | Core completo, sem brain |
| **v3** | Brain — grafo + embeddings | Core + Brain (brain adicionado) |
| **v4** | Brain-only — SQLite + ChromaDB + sleep | Core + Brain (brain é fonte primária) |

O **core** alcançou maturidade em v2. O brain é uma camada que se sobrepôs e hoje domina o workflow, mas o núcleo metacircular continua sendo DNA + Genesis + Evolution + Seeds + Agents + Commands.

---

## 5. Regra Prática para Modificações

**É core se:**
- Define *como* o Claude gera, valida ou orquestra componentes
- É universal (serve a qualquer projeto)
- Vive em `core/` no repositório fonte

**Não é core se:**
- É *onde* o conhecimento vive (grafo, embeddings)
- É específico de nicho (extras)
- É apenas scaffolding (templates)

---

## 6. Conclusão

O **core do projeto** é o **sistema metacircular**: DNA, Genesis, Evolution, Seeds, Agents e Commands. O cérebro é uma **feature extra** que surgiu em v3 e se tornou predominante no v4, mas conceitualmente não faz parte do núcleo — é a camada de memória que o core *consome* quando disponível.
