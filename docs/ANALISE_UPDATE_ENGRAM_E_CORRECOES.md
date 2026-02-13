# Análise: Correções e /update-engram

> auth-expert só em extras, fonte do update-backup, sem agent-bases, viabilidade do /update-engram.

---

## 1. auth-expert — Somente em extras

**Correção**: auth-expert.md deve ser criado **apenas** em `extras/agents/auth-expert.md`. Não em core/agents.

O plano já tinha isso na tabela de arquivos, mas havia referências a "core/agents" ou "agent-bases" que podiam sugerir duplicação. Remover todas as referências a auth-expert em core.

---

## 2. Fonte da informação ".claude.update-backup.{timestamp}"

**Origem**: Código do `setup.sh`, função `backup_for_update()` (linha ~719):

```bash
local BACKUP_DIR="$TARGET_DIR/.claude.update-backup.${TIMESTAMP}"
cp -r "$CLAUDE_DIR" "$BACKUP_DIR"
```

O **install** (quando já existe config) usa `.claude.bak` (linha ~536). O **update** usa `.claude.update-backup.{timestamp}`. São nomes diferentes.

---

## 3. Fluxo de backup — Verificar, processar, apagar

**Fluxo desejado pelo usuário**:
1. setup --update ou install (com config existente) cria backups
2. Usuário roda /init-engram (ou /update-engram)
3. Comando verifica backups, executa migração/prune/customize
4. **Ao final, apaga os backups** — próximo update não terá arquivos de backup

O `migrate_backup.py` já tem `--cleanup` que remove `.claude.bak` e `CLAUDE.md.bak`. A Fase 7 do init-engram chama isso quando houve migração. O fluxo está correto.

**Ponto**: Se o update usar `.claude.update-backup.{timestamp}`, o migrate_backup **não** detecta (ele só vê `.claude.bak`). Por isso a proposta de unificar. Ou: o migrate_backup passa a detectar também `.claude.update-backup.*`.

---

## 4. Sem agent-bases — Claude cria com inteligência

**Decisão**: 
- **core** não terá pasta `agent-bases`
- O projeto alvo não tem `core/`
- **Claude/Cursor** cria agents com base em comandos e inteligência
- O setup/init-engram analisa o projeto (tecnologias, conhecimento, padrões) para criar os melhores agents e skills
- Agents e skills são **específicos do projeto** — criados no projeto

**Fluxo**:
1. setup instala: core agents (architect, db-expert, domain-analyst) + extras (infra-expert, prompt-engineer, auth-expert) → `.claude/agents/`
2. init-engram: analyze_project detecta stack → prune (remove desnecessários) → create (scaffold para os que faltam) → **customize** (Claude produz conteúdo específico com base no projeto)

O `generate_component` para agents que não existem: **apenas scaffold genérico**. A customização é feita pelo Claude usando:
- analyze_project (stack, technologies, patterns)
- agent-customization-guide
- Conhecimento do projeto

Sem agent-bases. A inteligência está na customização, não em templates pré-definidos.

---

## 5. /update-engram — Viabilidade e vantagens

### 5.1 Responsabilidades hoje no init-engram

| Fase | Responsabilidade |
|------|------------------|
| 0 | Migração de backup (migrate_backup) |
| 1 | Análise do projeto |
| 2 | Apresentar plano |
| 3 | Auto-geração (skills, agents) |
| 4 | Popular knowledge |
| 5 | Popular cérebro |
| 6 | Health check |
| 7 | Cleanup (apagar backups) |

### 5.2 Separação de responsabilidades

**init-engram**: Inicialização **nova** — análise, geração, população. Foco em projeto que nunca teve Engram ou está sendo configurado do zero.

**update-engram**: Pós-**update** — quando o setup já rodou e criou backups. Foco em:
- Verificar backups (`.claude.bak` ou `.claude.update-backup.*`)
- Migrar conteúdo customizado
- Prune/customize agents (Fase 2.5)
- Apagar backups ao final

### 5.3 Vantagens do /update-engram

| Vantagem | Descrição |
|----------|-----------|
| **Clareza** | Um comando para init, outro para update — intenção explícita |
| **Menos acoplamento** | init-engram não precisa saber se veio de update ou install |
| **Fluxo mais enxuto** | update-engram só faz: Backup → Migrar → Agents → Cleanup |
| **Reutilização** | Partes do init-engram (analyze, prune, customize) podem ser chamadas pelo update-engram |
| **Testabilidade** | Cada comando pode ser testado isoladamente |

### 5.4 Desvantagens / Cuidados

| Ponto | Mitigação |
|-------|------------|
| Duplicação de lógica | update-engram chama scripts (migrate_backup, prune_agents) — mesma lógica |
| Dois comandos para aprender | Documentar: "Após setup --update, rode /update-engram" |
| Quando usar qual? | init-engram = primeira vez ou reconfigurar tudo; update-engram = após atualizar Engram |

### 5.5 Viabilidade

**Viável**: Sim. O update-engram seria um comando mais enxuto que:
1. Detecta backups
2. Roda migrate_backup (detect → analyze → migrate)
3. Roda analyze_project
4. Roda Fase 2.5 Agents (prune → create → customize)
5. Roda cleanup (apagar backups)

Não precisa repetir: popular knowledge, popular cérebro, health check completo — isso é init. O update só precisa "mesclar o que mudou e adequar agents".

### 5.6 Conclusão

**Recomendação**: Criar `/update-engram` como comando separado. O init-engram remove a Fase 0 (migrate_backup) ou a simplifica para "se backup existe, sugerir rodar /update-engram primeiro". O update-engram concentra a lógica pós-update.
