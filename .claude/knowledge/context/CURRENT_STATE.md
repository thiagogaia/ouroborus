# Estado Atual do Projeto
> Última atualização: 2026-02-03 (Arquitetura Git-Native v3.0 aprovada)

## Status Geral
- **Fase**: Arquitetura v3.0 — Git-native com grafo de conhecimento definida
- **Saúde**: 🟢 Saudável (Health Score 100%)
- **Próximo Marco**: Implementar estrutura de arquivos escalável

## Identidade
**Engram v2** — Sistema metacircular de memória persistente para Claude Code.
O sistema que gera a si mesmo (ouroboros).

## Arquitetura Core

### Diretórios Principais
```
engram/
├── core/                          # DNA do sistema (copiado para projetos)
│   ├── schemas/                   # Definições formais de componentes
│   ├── genesis/                   # Motor de auto-geração (SKILL.md + scripts/)
│   ├── evolution/                 # Motor de evolução (SKILL.md + scripts/)
│   ├── seeds/                     # Skills universais
│   ├── agents/                    # Templates de agents
│   └── commands/                  # Slash commands
├── templates/                     # Templates de stacks (nextjs, django, etc)
│   ├── knowledge/                 # Templates de knowledge files
│   └── stacks/                    # Templates por framework
├── extras/                        # Skills/agents opcionais
├── setup.sh                       # Instalador principal
└── docs/                          # Documentação
```

### Fluxo de Dados
```
setup.sh → instala DNA (schemas) + genesis + evolution + seeds
              ↓
/init-engram → genesis analisa projeto → gera skills customizados
              ↓
/learn → evolution rastreia uso → propõe melhorias
              ↓
genesis → evolui componentes → ciclo recomeça
```

## Componentes Instalados

### Skills Core (2)
| Nome | Função | Scripts |
|------|--------|---------|
| engram-genesis | Motor de auto-geração | analyze_project.py, generate_component.py, validate.py, register.py, compose.py, migrate_backup.py |
| engram-evolution | Motor de evolução | track_usage.py, doctor.py, archive.py, curriculum.py, co_activation.py, global_memory.py |

### Seeds (6 skills universais)
| Nome | Função |
|------|--------|
| project-analyzer | Análise profunda de codebase |
| knowledge-manager | Gerencia feedback loop |
| domain-expert | Descoberta de regras de negócio |
| priority-engine | Priorização com ICE Score |
| code-reviewer | Code review em 4 camadas |
| engram-factory | Orquestração runtime |

### Agents (3)
| Nome | Especialidade |
|------|---------------|
| architect | Decisões arquiteturais, ADRs |
| db-expert | Schema, queries, migrations |
| domain-analyst | Regras de negócio, glossário |

### Commands (13)
/init-engram, /status, /plan, /commit, /review, /priorities, /learn, /create, /spawn, /doctor, /curriculum, /export, /import

## O Que Mudou Recentemente
- [2026-02-03] **[[ADR-008]]**: Arquitetura Git-Native com Grafo de Conhecimento aprovada | Impacto: CRÍTICO
- [2026-02-03] **[[ADR-009]]**: Estado por Desenvolvedor (state/dev.md) aprovado | Impacto: ALTO
- [2026-02-03] **[[ADR-010]]**: Convenção de Commits de Conhecimento aprovada | Impacto: MÉDIO
- [2026-02-03] Análise de escalabilidade: 10 devs × 5 anos = viável com camadas | Impacto: ALTO
- [2026-02-03] Modelo Obsidian ([[wikilinks]] + backlinks) adotado | Impacto: ALTO
- [2026-02-03] Sistema de migração de backups implementado (migrate_backup.py) | Impacto: ALTO

## Dívidas Técnicas
| Item | Severidade | Descrição |
|------|------------|-----------|
| DT-001 | 🟡 Baixa | Falta coverage de testes nos scripts Python |
| DT-002 | 🟡 Baixa | Templates de stack incompletos (só 7 frameworks) |
| DT-003 | 🟢 Info | Documentação poderia ter mais exemplos |

## Bloqueios Conhecidos
Nenhum bloqueio ativo.

## Métricas de Uso (acumulado)
| Componente | Ativações | Status |
|------------|-----------|--------|
| engram-genesis | 2 | 🟢 Ativo |
| engram-evolution | 3 | 🟢 Ativo |
| python-scripts | 1 | 🟢 Novo |
| project-analyzer | 2 | 🟢 Ativo |
| architect | 0 | ⚪ Não usado |
| db-expert | 0 | ⚪ Não usado |
| domain-analyst | 0 | ⚪ Não usado |

## Contexto Para Próxima Sessão

### Arquitetura v3.0 Aprovada
A nova arquitetura para escalabilidade foi definida em [[ADR-008]], [[ADR-009]], [[ADR-010]]:

**Estrutura de Arquivos Escalável:**
```
.claude/
├── active/              ← HOT (últimos 90 dias)
│   ├── state/           ← 1 arquivo POR DEV
│   ├── episodes/        ← 1 arquivo por episódio com [[links]]
│   ├── patterns/        ← 1 arquivo por pattern
│   ├── decisions/       ← 1 arquivo por ADR
│   ├── concepts/        ← glossário linkável [[conceito]]
│   └── people/          ← [[@pessoa]] sabe o quê
├── consolidated/        ← summaries trimestrais
├── archive/             ← episódios > 90 dias
├── graph/               ← backlinks.json (grafo unificado)
└── scripts/             ← automação
```

**Simplificação:** INDEX.md eliminado. O grafo (backlinks.json) com `views`
pré-computadas serve como índice. Estratégia Obsidian pura.

**Modelo de Links (Obsidian):**
- `[[conceito]]` → concepts/conceito.md
- `[[@pessoa]]` → people/pessoa.md
- `[[ADR-NNN]]` → decisions/ADR-NNN.md
- Backlinks gerados automaticamente

**Escalabilidade Comprovada:**
- 10 devs × 5 anos = ~25k episódios = ~50MB
- Git aguenta tranquilo
- Tokens sob controle: ~$0.20/sessão (vs $37 sem otimização)
- Consolidation job compacta episódios antigos

### Próximos Passos de Implementação
1. [ ] Criar estrutura de diretórios (active/, consolidated/, archive/, graph/)
2. [ ] Migrar conhecimento atual para novo formato com [[links]]
3. [ ] Implementar build_graph.py (gera backlinks.json com views)
4. [ ] Implementar consolidate.py (job mensal)
5. [ ] Atualizar templates com convenção de [[links]]
6. [ ] Integrar build_graph no /learn
7. [ ] Testar com 2-3 devs em projeto real
