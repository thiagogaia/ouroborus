# Planejamento Final — Agents: Prune, Spawn, Customize

> Versão consolidada para verificação de assertividade. Todas as correções aplicadas.

---

## 1. Visão Geral

### 1.1 Fluxo

```
setup.sh (install)     → core + extras (install_extras.sh)
setup.sh (update)      → core + extras + backup (.claude.bak, CLAUDE.md.bak)
        ↓
/init-engram           → Inicialização nova (análise, geração, knowledge, cérebro)
/update-engram         → Pós-update (backup → migrar → prune/customize → apagar backups)
        ↓
Fase Agents:
  analyze_project → prune_agents → create (scaffold) → customize (Claude)
```

### 1.2 Decisões consolidadas

| Decisão | Valor |
|---------|-------|
| auth-expert | Somente em `extras/agents/auth-expert.md` |
| agent-bases | Não criar. Scaffold + customização por Claude |
| Backup | Unificado: `.claude.bak/` e `CLAUDE.md.bak` (install e update) |
| /update-engram | Criar comando separado — viável e recomendado |

---

## 2. O que já está implementado

| Item | Status |
|------|--------|
| Extras no setup (install + update) | ✅ Feito |
| Backup unificado no update | ✅ Feito |

---

## 3. Ordem de implementação

| # | Tarefa | Arquivos | Status |
|---|--------|----------|--------|
| 0 | Extras no setup | setup.sh | ✅ Feito |
| 0b | Backup unificado no update | setup.sh | ✅ Feito |
| 1 | Criar prune_agents.py | core/genesis/scripts/prune_agents.py | Pendente |
| 2 | Aprimorar analyze_project: customization | analyze_project.py | Pendente |
| 3 | Aprimorar analyze_project: auth-expert, infra-expert | analyze_project.py | Pendente |
| 4 | generate_component: scaffold apenas | generate_component.py | Pendente |
| 5 | Criar auth-expert | extras/agents/auth-expert.md | Pendente |
| 6 | Criar agent-customization-guide.md | core/genesis/references/ | Pendente |
| 7 | Integrar init-engram: Fase 2.5 Agents | core/commands/init-engram.md | Pendente |
| 8 | Criar comando /update-engram | core/commands/update-engram.md | Pendente |

---

## 4. Arquivos a criar/modificar

| Arquivo | Ação |
|---------|------|
| setup.sh | ✅ Feito (extras + backup unificado) |
| core/genesis/scripts/prune_agents.py | Criar |
| core/genesis/scripts/analyze_project.py | Modificar |
| core/genesis/scripts/generate_component.py | Modificar (nenhuma mudança se já usa scaffold) |
| extras/agents/auth-expert.md | Criar |
| core/genesis/references/agent-customization-guide.md | Criar |
| core/commands/init-engram.md | Modificar |
| core/commands/update-engram.md | Criar |

---

## 5. Fluxo de backup (unificado)

**Install** (quando já existe config):
- `.claude/` → `.claude.bak/`
- `CLAUDE.md` → `CLAUDE.md.bak`

**Update**:
- `.claude/` → `.claude.bak/`
- `CLAUDE.md` → `CLAUDE.md.bak` (se existir)

**Pós-update/init**: migrate_backup detecta, migra, e --cleanup apaga os backups ao final.

---

## 6. Comandos

| Comando | Quando usar | O que faz |
|---------|-------------|-----------|
| **/init-engram** | Primeira instalação ou criar tudo do zero | Se backup existir: **alerta** (coisas serão perdidas) e sugere /update-engram. Caso contrário: análise, geração, knowledge, cérebro. |
| **/update-engram** | Após `setup.sh --update` | Detectar backup → migrar → prune/customize agents → **apagar backups** |

---

## 7. Agents

### 7.1 Origens

- **core/agents/**: architect, db-expert, domain-analyst
- **extras/agents/**: infra-expert, prompt-engineer, **auth-expert** ( único em extras)

### 7.2 Fase 2.5 (init-engram e update-engram)

1. agents_needed = analyze_project
2. agents_existing = listar .claude/agents/*.md
3. to_remove = existing - needed → prune_agents
4. to_create = needed - existing → generate_component (scaffold)
5. to_keep ∪ to_create → Claude customiza (agent-customization-guide)
6. validate + register

---

## 8. Riscos e mitigações

| Risco | Mitigação |
|-------|-----------|
| Customização inconsistente | agent-customization-guide + checklist |
| prune remove agent customizado | Confirmação antes de prune |
| validate falha | Claude corrige antes de registrar |

---

## 9. Checkpoints de assertividade

- [ ] auth-expert existe **apenas** em extras/agents/
- [ ] core **não** tem agent-bases/
- [ ] setup --update usa .claude.bak (não .claude.update-backup.*)
- [ ] migrate_backup detecta e processa .claude.bak
- [ ] Backup é apagado ao final (--cleanup)
- [ ] /update-engram tem responsabilidades claras vs /init-engram
- [ ] generate_component usa apenas scaffold quando agent não existe
