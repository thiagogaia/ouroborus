# Análise Final — Fluxo e Plano de Implementação

> Consolidação das decisões e plano unificado para implementação.

---

## 1. Decisões Consolidadas

| # | Decisão | Ação |
|---|---------|------|
| 1 | **setup.sh --update** | Manter como está. Funciona bem: preserva brain, knowledge, agents custom. |
| 2 | **/update-engram** | Remover. Comando não mais necessário. |
| 3 | **Brain** | Sempre manter o brain do projeto alvo. Setup --update já preserva; nunca substituir por backup. |
| 4 | **Backup + merge** | Opção B: init-engram, ao detectar backup, faz merge (quando fizer sentido) e cleanup dos backups. |
| 5 | **memory/** | Residual. Não criar nem migrar. Tudo fica no cérebro. |

---

## 2. Fluxo Final Unificado

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ setup.sh (install)                                                          │
│   Se .claude/ ou CLAUDE.md existem → backup (.claude.bak, CLAUDE.md.bak)   │
│   → install_core (sobrescreve .claude/)                                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                      ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│ setup.sh --update (projeto já com Engram)                                   │
│   → backup (.claude.bak, CLAUDE.md.bak)                                     │
│   → atualiza core (dna, genesis, evolution, seeds, agents, commands)       │
│   → preserva: knowledge/, brain (dados), manifest                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                      ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│ /init-engram — único ponto de entrada pós-setup                             │
│                                                                             │
│   Se backup existe:                                                          │
│     0. Fase 0.5: Merge do backup (IA decide estratégia)                     │
│        • agents, skills, knowledge: merge/substituir conforme análise      │
│        • brain: NUNCA tocar (manter do projeto)                             │
│        • cleanup: apagar .claude.bak e CLAUDE.md.bak                         │
│   Se backup não existe:                                                     │
│     → prossegue direto para Fase 1                                          │
│                                                                             │
│   Fase 1: Análise do projeto                                                │
│   Fase 2: Apresentar plano                                                 │
│   Fase 2.5: Agents — prune, create, customize                              │
│   Fase 3: Skills — generate, customize                                     │
│   Fase 4: Popular knowledge                                                │
│   Fase 5: Popular cérebro (se vazio) ou pular se já populado                │
│   Fase 6: Health check                                                     │
│   Fase 7: Cleanup (templates) + relatório                                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Fase 0.5: Merge do Backup (novo)

Quando `migrate_backup.py --detect` retorna `found: true`:

### 3.1 Input para a IA

1. Executar `migrate_backup.py --analyze --output json`
2. Comparar backup vs `.claude/` atual (o que o setup acabou de instalar/atualizar)

### 3.2 O que mergear

| Componente | Estratégia | Regra |
|------------|------------|-------|
| **agents** | IA decide | Compare backup vs atual. Se backup tem customização que foi sobrescrita (ex.: architect customizado), considerar merge. Se backup tem agents que não existem no atual (ex.: auth-expert), copiar. |
| **skills** | IA decide |同上. Skills customizados no backup que não existem no core → preservar. |
| **commands** | IA decide |同上. |
| **knowledge** | IA decide | merge_knowledge_file (EXPERIENCE, PATTERNS, ADR, DOMAIN) — append entradas únicas. |
| **settings** | merge | Permissões customizadas do backup → adicionar ao atual. |
| **brain** | **NUNCA** | Manter o brain do projeto. Não copiar brain.db nem embeddings do backup. |
| **CLAUDE.md** | IA decide | Regras customizadas, seções extras do backup → mesclar se relevantes. |

### 3.3 Uso do migrate_backup.py

O script já tem:
- `--analyze`: retorna custom_skills, custom_commands, custom_agents, knowledge com conteúdo
- `--migrate --strategy smart`: merge settings, preserve custom components, merge knowledge
- `--cleanup`: apaga backups

A IA pode:
- Usar `--analyze` para decisão
- Chamar `--migrate` quando fizer sentido (ou executar merge manualmente para casos específicos)
- Chamar `--cleanup` ao final

### 3.4 Ordem

1. analyze
2. IA decide e aplica merge (ou delega ao migrate_backup)
3. cleanup

---

## 4. Remoção do /update-engram

### 4.1 Arquivos removidos ✅

- `core/commands/update-engram.md` — removido
- `.claude/commands/update-engram.md` — removido

### 4.2 Referências a atualizar

| Arquivo | Ação |
|---------|------|
| `core/commands/init-engram.md` | Substituir menção a update-engram por Fase 0.5 (merge + cleanup) |
| `setup.sh` | Linha 1011: corrigir mensagem "vai mergear" → "Use /init-engram para completar" |
| `docs/PLANO_IMPLEMENTACAO_AGENTS_PRUNE_SPAWN_CUSTOMIZE.md` | Remover update-engram do fluxo; atualizar para init-engram único |
| `docs/PLANEJAMENTO_FINAL_AGENTS_PRUNE_SPAWN_CUSTOMIZE.md` | 同上 |
| `CLAUDE.md` | Se mencionar update-engram, remover ou atualizar |

---

## 5. Plano de Implementação Revisado

### 5.1 Ordem de tarefas (consolidada)

| # | Tarefa | Arquivos | Dependências |
|---|--------|----------|--------------|
| **A** | **Remover update-engram** | core/commands/, .claude/commands/ | — |
| **B** | **Inserir Fase 0.5 no init-engram** | core/commands/init-engram.md | migrate_backup.py (já existe) |
| **C** | **Corrigir setup.sh verify_installation** | setup.sh | — |
| **1** | Criar prune_agents.py | core/genesis/scripts/ | register.py |
| **2** | Aprimorar analyze_project: customization | analyze_project.py | — |
| **3** | Aprimorar analyze_project: auth-expert, infra-expert | analyze_project.py | — |
| **4** | Verificar generate_component (scaffold, sem agent-bases) | generate_component.py | — |
| **5** | Criar auth-expert (base) | extras/agents/auth-expert.md | — |
| **6** | Criar agent-customization-guide.md | core/genesis/references/ | — |
| **7** | Integrar Fase 2.5 Agents no init-engram | init-engram.md | 1–6 |
| **8** | Atualizar docs e referências | PLANO, PLANEJAMENTO_FINAL | A–C |

### 5.2 Dependências

- **A, B, C**: podem ser feitos em paralelo ou na ordem A → B → C
- **1–6**: ordem sugerida (prune primeiro, depois analyze, guide)
- **7**: depende de 1–6
- **8**: após A–C e 7

---

## 6. Conteúdo da Fase 0.5 (init-engram.md)

Texto sugerido para inserir no init-engram:

```markdown
## Fase 0.5: Merge do Backup (quando backup existe)

Se `found: true` na detecção, **não** avisar para usar update-engram. Executar merge.

1. Executar análise:
```bash
python3 .claude/skills/engram-genesis/scripts/migrate_backup.py --project-dir . --analyze --output json
```

2. Com base no resultado, decidir estratégia para cada categoria:
   - **agents**: preservar custom do backup que não existem no atual; para core agents sobrescritos, avaliar se backup tem customização a preservar
   - **skills**: preservar custom do backup
   - **commands**: preservar custom do backup
   - **knowledge**: merge (append entradas únicas de EXPERIENCE, PATTERNS, ADR, DOMAIN)
   - **settings**: merge permissões customizadas
   - **brain**: NUNCA tocar — manter o brain do projeto

3. Executar merge (usar migrate_backup --migrate ou aplicar manualmente conforme análise):
```bash
python3 .claude/skills/engram-genesis/scripts/migrate_backup.py --project-dir . --migrate --strategy smart
```

4. Após merge confirmado, cleanup:
```bash
python3 .claude/skills/engram-genesis/scripts/migrate_backup.py --project-dir . --cleanup
```

5. Prosseguir para Fase 1.
```

---

## 7. Riscos e Mitigações

| Risco | Mitigação |
|-------|-----------|
| Merge incorreto perde customização | IA analisa antes de aplicar; migrate_backup tem strategy smart |
| Brain substituído por engano | Regra explícita: NUNCA tocar brain. Nunca chamar cleanup de brain. |
| Backup removido antes de merge completo | Cleanup só ao final, após merge confirmado |
| Usuário espera update-engram | Documentar: "Após setup --update, rode /init-engram" |

---

## 8. Checklist Pré-Implementação

- [ ] Decisões 1–5 aprovadas
- [ ] Fluxo unificado (seção 2) compreendido
- [ ] Fase 0.5 (seção 6) aprovada
- [ ] Ordem de tarefas (seção 5.1) aceita
- [ ] Início da implementação: tarefas A, B, C (remoção + Fase 0.5 + correção setup)

---

## 9. Resumo Executivo

**O que muda:**
- `/update-engram` removido
- `/init-engram` absorve: ao detectar backup → Fase 0.5 (merge + cleanup)
- Brain sempre preservado; nunca migrado do backup

**O que permanece:**
- setup.sh (install e --update) sem alteração
- Fluxo de agents (prune, create, customize) no init-engram Fase 2.5
- PLANO de implementação (prune_agents, analyze_project, auth-expert, agent-customization-guide) mantido

**Próximo passo:** Aprovar esta análise e iniciar implementação (tarefas A, B, C).
