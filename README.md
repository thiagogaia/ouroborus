<p align="center">
  <img src="logo.svg" width="180" alt="Engram"/>
</p>

<h1 align="center">Engram v2</h1>

<p align="center">
  <strong>Self-evolving persistent memory for Claude Code.</strong><br/>
  <em>Each session ends smarter than it started. The system generates itself.</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/claude--code-compatible-6366f1?style=flat-square" alt="Claude Code"/>
  <img src="https://img.shields.io/badge/metacircular-self--generating-8b5cf6?style=flat-square" alt="Metacircular"/>
  <img src="https://img.shields.io/badge/seeds-6-a78bfa?style=flat-square" alt="Seeds"/>
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License"/>
</p>

---

## What is it

Engram transforms Claude Code into an agent that **learns from each session** and **evolves its own capabilities**. It installs a metacircular system of skills, agents, commands and knowledge files that self-generate and self-improve — the [Ouroboros](https://en.wikipedia.org/wiki/Ouroboros) of AI.

### v1 → v2: What changed

| Aspect | v1 | v2 (metacircular) |
|--------|----|--------------------|
| Installation | Copies fixed skills | Installs DNA + genesis engine |
| Skills | 5 universal, manual extras | 6 seeds + N auto-generated per project |
| Evolution | Manual (dev edits) | Automatic proposals (genesis + evolution) |
| Validation | None | Schema-driven + `validate.py` |
| Tracking | None | Manifest with usage metrics & health |
| Versioning | None | Automatic archive + restore |
| Pruning | None | Evolution detects & retires stale components |

## How it works

```
┌─ INSTALL (setup.sh) ─────────────────────────────────┐
│                                                        │
│  Detects stack → installs DNA (schemas) + genesis     │
│  + seed skills + knowledge templates                   │
│                                                        │
├─ GENESIS (/init-engram) ──────────────────────────────┤
│                                                        │
│  Genesis analyzes project → generates custom skills,  │
│  agents and commands → validates against schemas      │
│  → registers in manifest                              │
│                                                        │
├─ USE (daily work) ────────────────────────────────────┤
│                                                        │
│  Skills loaded on demand (progressive disclosure)     │
│  Agents forked for specialized tasks                  │
│  Commands for frequent operations                     │
│                                                        │
├─ EVOLVE (/learn) ─────────────────────────────────────┤
│                                                        │
│  Records knowledge → tracks component usage           │
│  → detects patterns → proposes new skills             │
│  → retires stale ones → versions changes              │
│                                                        │
└────── 🐍 cycle repeats, each time better ─────────────┘
```

## Quick Start

### 1. Clone

```bash
git clone https://github.com/your-user/engram.git ~/engram
```

### 2. Install

```bash
cd ~/engram
./setup.sh /path/to/your/project
```

The installer detects your stack automatically:

| Detects | Examples |
|---------|----------|
| Language | Node.js, Python, PHP, Rust, Go, Ruby |
| Framework | Next.js, React, Vue, Angular, Django, Laravel, FastAPI |
| ORM | Prisma, Drizzle, TypeORM, Sequelize |
| Database | PostgreSQL, MySQL, MongoDB, SQLite, Supabase |
| UI | shadcn/ui, MUI, Chakra, Tailwind |
| Auth | NextAuth, Clerk, Lucia, Better Auth |
| Tests | Vitest, Jest, Playwright, Cypress |
| Infra | Docker, package manager, monorepo |

### 3. Generate with AI

```bash
cd /your/project
claude
/init-engram
```

Claude uses the **genesis skill** to analyze your project, generate custom skills/agents, populate knowledge files, and run a health check. No two installations are the same.

### 4. Use

| Command | What it does |
|---------|--------------|
| `/status` | Project state, priorities, next action |
| `/plan [feature]` | Implementation plan with steps |
| `/review` | Code review of changed files |
| `/priorities` | Re-evaluate priorities with ICE Score |
| `/learn` | **Record knowledge + evolve system** |
| `/commit` | Semantic git commit |
| `/create [type] [name]` | Generate new skill, agent, or command |
| `/spawn [type] [name]` | **Fast runtime creation** mid-task |
| `/doctor` | Health check of the Engram installation |
| `/curriculum` | Skill coverage analysis + suggestions |
| `/export [type] [name]` | Export skill/pattern/experience to global memory |
| `/import [name]` | Import skill from global memory |

## Architecture

```
your-project/
├── CLAUDE.md                          # Main instructions (generated)
└── .claude/
    ├── manifest.json                  # Component registry + metrics
    ├── settings.json                  # Permissions
    ├── schemas/                       # 🧬 DNA — formal component definitions
    │   ├── skill.schema.md
    │   ├── agent.schema.md
    │   ├── command.schema.md
    │   └── knowledge.schema.md
    │
    ├── skills/                        # 🎯 Capabilities
    │   ├── engram-genesis/            #    🧬 Self-generation engine
    │   │   ├── SKILL.md
    │   │   ├── scripts/              #    analyze, generate, validate, register
    │   │   └── references/           #    patterns + anti-patterns
    │   ├── engram-evolution/          #    🔄 Self-evolution engine
    │   │   ├── SKILL.md
    │   │   ├── scripts/              #    track_usage, archive
    │   │   └── references/           #    evolution-log
    │   ├── project-analyzer/          #    Codebase analysis
    │   ├── knowledge-manager/         #    Feedback loop engine
    │   ├── domain-expert/             #    Business domain knowledge
    │   ├── priority-engine/           #    ICE Score prioritization
    │   ├── code-reviewer/             #    4-layer code review
    │   └── [auto-generated]/          #    Project-specific (by genesis)
    │
    ├── agents/                        # 🤖 Specialists (generated by /init-engram)
    ├── commands/                      # ⚡ Slash commands
    ├── versions/                      # 📦 Component version archive
    │
    └── knowledge/                     # 📚 Persistent memory
        ├── context/CURRENT_STATE.md   #    Living project state
        ├── priorities/PRIORITY_MATRIX.md  #  Tasks with ICE Score
        ├── patterns/PATTERNS.md       #    Discovered patterns
        ├── decisions/ADR_LOG.md       #    Architectural decisions
        ├── domain/DOMAIN.md           #    Business glossary & rules
        └── experiences/EXPERIENCE_LIBRARY.md  # Reusable solutions
```

## Metacircular Self-Generation

Engram v2 contains the capacity to generate itself:

1. **Schemas** define what valid components look like (the DNA)
2. **Genesis** generates components that conform to schemas
3. **Evolution** tracks usage and proposes improvements
4. Genesis can generate updated versions of itself (metacircular)

```
Schema defines → Genesis generates → Evolution measures → Genesis evolves
       ↑                                                        │
       └────────────────────────────────────────────────────────┘
```

## Seeds vs Generated

**Seeds** (5) ship with every installation — universal capabilities:
project-analyzer, knowledge-manager, domain-expert, priority-engine, code-reviewer.

**Generated** skills are created by genesis during `/init-engram` based on your
specific stack. A Next.js + Prisma project gets `nextjs-patterns` and
`prisma-workflow`. A Django project gets `django-patterns`. No two setups are alike.

## The Evolution Cycle

During `/learn`, the evolution skill:
- Tracks which components were used this session
- Detects stale components (never/rarely used) → proposes archive
- Detects recurring patterns without skill → proposes creation
- Detects skills always used together → proposes composition
- Versions any modified component before changing it

## Runtime Orchestration

Claude creates subagents and skills **on the fly** when a task requires expertise
that no existing component covers. No need to stop and run `/create` manually.

```
Claude receives task
  → "Do I have a specialist for this?"
  → Lists agents/ and skills/
  → NO match found
  → "⚡ Creating agent oracle-migration-expert for this task"
  → Genesis: generate → customize → validate → register (source: runtime)
  → Delegates task to the new agent
  → Reports what was created
```

Runtime components are tagged `source: runtime` in the manifest. During `/learn`,
Claude evaluates each one: keep (useful), archive (one-off), or merge (overlaps
with existing). Use `/spawn` for explicit fast creation mid-task.

## CLI Options

```bash
./setup.sh                      # Install in current directory
./setup.sh /path/to/project     # Install in specific directory
./setup.sh --update .           # Update core, keep knowledge
./setup.sh --uninstall .        # Remove Engram cleanly
./setup.sh --help               # Show help
./setup.sh --version            # Show version
```

## Extras

The `extras/` folder contains niche skills/agents not installed by default:

| Extra | Type | Description |
|-------|------|-------------|
| `n8n-agent-builder` | Skill | Multi-agent architecture for N8N + WhatsApp |
| `sales-funnel-optimizer` | Skill | Sales funnel optimization |
| `prompt-engineer` | Agent | Prompt engineering for conversational agents |

To install:
```bash
cp -r ~/engram/extras/skills/n8n-agent-builder your-project/.claude/skills/
cp ~/engram/extras/agents/prompt-engineer.md your-project/.claude/agents/
```

## .gitignore Guidance

**Commit everything** in `.claude/` — this is your project's memory:
```
# DO commit:
.claude/knowledge/    # Persistent memory
.claude/skills/       # All skills (seeds + generated)
.claude/agents/       # All agents
.claude/commands/     # All commands
.claude/schemas/      # Component schemas
.claude/manifest.json # Component registry
.claude/settings.json # Permissions
CLAUDE.md             # Main instructions

# DON'T commit (auto-generated, optional):
.claude/versions/     # Component backups (optional — useful for history)
.claude.bak/          # Installation backup (remove after /init-engram)
CLAUDE.md.bak         # Installation backup
```

## Principles

1. **Metacircular** — The system generates and evolves itself
2. **Schema-driven** — Components are correct by construction
3. **Knowledge-first** — If it's not recorded, it didn't happen
4. **Progressive disclosure** — Skills load on demand, not all at once
5. **Aggressive deprioritization** — As important as prioritization
6. **Evolution over revolution** — Small improvements compound

## Why "Engram"?

> **Engram** (neuroscience): the physical trace of a memory stored in the brain.
> The fundamental unit of learned information that persists between states of consciousness.

The **Ouroboros** icon 🐍 represents the feedback cycle: each session consumes
knowledge from the previous one and produces knowledge for the next.

## License

MIT
