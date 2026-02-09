# Análise Final — Setup, Update, Brain e Implementação

> Verificação completa antes da implementação. Cobrir: backup vs update automático, fresh install, update apenas novas features, migração do brain.

---

## 1. Pergunta Central: Backup sempre ou Rodar Update quando existir?

### Opção A: Sempre backup + full install (comportamento atual do install)

**Fluxo:** `./setup.sh` em projeto com `.claude/` → backup → install_core (sobrescreve tudo)

| Vantagens | Desvantagens |
|-----------|--------------|
| Simples, previsível | Projeto existente perde customizações (agents, knowledge) |
| Sem ambiguidade | Depende do init-engram para recuperar do backup |
| Install = sempre “instalação do zero” | Usuário pode rodar por engano e sobrescrever |

### Opção B: Detectar e rodar update quando existir

**Fluxo:** `./setup.sh` em projeto com `.claude/` → **detectar** → rodar fluxo de update (preservar dados) em vez de install

| Vantagens | Desvantagens |
|-----------|--------------|
| Comportamento “inteligente” | Duas lógicas no mesmo comando |
| Protege projetos existentes | “Reinstalar do zero” exige flag (ex: `--force-reinstall`) |
| Um comando para install e update | Pode confundir quem espera “sempre install” |

### Recomendação: **Opção A mantida + documentação clara**

- **install**: backup se existir → full install. Mensagem explícita: “Se o projeto já tinha Engram, rode `/init-engram` para merge do backup.”
- **update**: `./setup.sh --update` — uso explícito para atualização.
- Motivo: intenção do usuário fica clara (install vs update). Evita “magic” que pode surpreender.

---

## 2. Fresh Install — Objetivo

**Objetivo:** instalação completa e criação correta de agents e skills por projeto.

| Componente | Responsável | Comportamento |
|------------|-------------|---------------|
| Base (dna, genesis, evolution, seeds) | setup.sh | Copia do core |
| Agents core (architect, db-expert, domain-analyst) | setup.sh | Copia inicial |
| Customização (agents, skills) | **/init-engram** | analyze_project → prune → create → customize |
| Knowledge | init-engram Fase 4 | Popula a partir da análise |
| Cérebro | init-engram Fase 5 | populate.py + embeddings |

**Conclusão:** setup.sh entrega a base; init-engram faz a parte inteligente por projeto. Está alinhado com o objetivo.

---

## 3. Update — Estratégia “apenas novas features”

Atualmente o update **sobrescreve** core agents e seeds:

```bash
cp "$SCRIPT_DIR/core/agents/"*.md "$CLAUDE_DIR/agents/"   # sobrescreve
cp -r "${seed%/}" "$CLAUDE_DIR/skills/$SEED_NAME"         # sobrescreve
```

Problema: agents customizados (ex.: architect com Prisma) são substituídos pelas versões “virgens” do core.

### Proposta: update aditivo

| Componente | Comportamento atual | Comportamento proposto |
|------------|---------------------|------------------------|
| **dna, genesis, evolution** | Sobrescreve | Manter (são código, não customização) |
| **core agents** | Sobrescreve | **Não sobrescrever** — só adicionar se não existir |
| **seeds (skills)** | Sobrescreve | **Não sobrescrever** — só adicionar seeds novos |
| **extras** | install_extras (skip se existe) | Manter (já preserva) |
| **brain** | Preserva dados | Manter |
| **knowledge** | Não mexe | Manter |

Implementação sugerida:

```bash
# Agents: só adicionar os que não existem
for agent in "$SCRIPT_DIR/core/agents/"*.md; do
    [[ -f "$agent" ]] || continue
    name=$(basename "$agent")
    dest="$CLAUDE_DIR/agents/$name"
    if [[ ! -f "$dest" ]]; then
        cp "$agent" "$dest"
        print_done "Agent adicionado: $name"
    else
        print_warn "Agent existente preservado: $name"
    fi
done

# Seeds: idem — só adicionar novos
for seed in "$SCRIPT_DIR/core/seeds"/*/; do
    SEED_NAME=$(basename "$seed")
    DEST_SEED="$CLAUDE_DIR/skills/$SEED_NAME"
    if [[ ! -d "$DEST_SEED" ]]; then
        cp -r "${seed%/}" "$DEST_SEED"
        print_done "Seed adicionado: $SEED_NAME"
    else
        # atualizar arquivos do core (SKILL.md, scripts) mas preservar customizações locais?
        # Opção conservadora: não tocar
        print_warn "Seed existente preservado: $SEED_NAME"
    fi
done
```

Efeito: update passa a ser “apenas novas features”, sem sobrescrever customizações.

---

## 4. Brain — Migração automática de schema

### Estado atual

```python
# brain_sqlite.py
def _init_schema(self):
    conn.executescript(SCHEMA_SQL)   # CREATE TABLE IF NOT EXISTS
    conn.execute("INSERT OR IGNORE INTO meta (key, value) VALUES ('schema_version', ?)", (SCHEMA_VERSION,))
```

- Usa `CREATE TABLE IF NOT EXISTS` — não altera tabelas existentes.
- Não há lógica de migração (ALTER TABLE, novas colunas, etc.).
- Se o schema for alterado (novas colunas/tabelas), `brain.db` antigo **não** é atualizado.

### Necessidade de migração

Se houver mudanças de schema (ex.: nova coluna em `nodes`), é preciso:

1. Ler `schema_version` na tabela `meta`.
2. Aplicar migrações incrementais (ex.: v1→v2, v2→v3).
3. Atualizar `schema_version` em `meta`.

### Proposta de migração

```python
MIGRATIONS = {
    "1": [
        # Se precisar migrar de v1 para v2
        "ALTER TABLE nodes ADD COLUMN new_field TEXT;",
    ],
    "2": [
        # Futuras migrações v2→v3
    ],
}

def _run_migrations(self):
    conn = self._get_conn()
    row = conn.execute("SELECT value FROM meta WHERE key='schema_version'").fetchone()
    current = row[0] if row else "1"
    while current != SCHEMA_VERSION:
        next_ver = str(int(current) + 1)  # ou mapeamento explícito
        if next_ver not in MIGRATIONS:
            break
        for sql in MIGRATIONS[next_ver]:
            conn.execute(sql)
        conn.execute("UPDATE meta SET value=? WHERE key='schema_version'", (next_ver,))
        conn.commit()
        current = next_ver
```

Chamada: `_init_schema()` → `_run_migrations()` após criar tabelas.

### Prioridade

- Hoje o schema é estável (v2).
- Migração automática é **recomendada** para evoluções futuras.
- Pode ser implementada em uma etapa posterior, com ADR documentando o processo.

---

## 5. Resumo de decisões

| # | Decisão | Ação |
|---|---------|------|
| 1 | **Backup vs update automático** | Manter Opção A: install sempre faz backup + full install. Update explícito com `--update`. |
| 2 | **Fresh install** | setup.sh instala base; init-engram faz análise e customização por projeto. |
| 3 | **Update = novas features** | Alterar update para **não sobrescrever** agents e seeds existentes; só adicionar os que faltam. |
| 4 | **Brain migration** | Schema estável hoje. Implementar migração automática quando houver mudanças de schema (backlog). |
| 5 | **Brain no update** | Manter preservação de dados (não sobrescrever brain.db, embeddings). |

---

## 6. Fluxo final consolidado

```
./setup.sh [DIR]                    # Install (fresh ou reinstall)
  ├─ Se .claude/ ou CLAUDE.md existem → backup
  └─ install_core (sobrescreve)
  └─ "Rode /init-engram para completar"

./setup.sh --update [DIR]           # Update (projeto já com Engram)
  ├─ backup
  ├─ Atualiza: dna, genesis, evolution (sempre)
  ├─ Agents: só ADICIONA os que não existem (não sobrescreve)
  ├─ Seeds: só ADICIONA os que não existem (não sobrescreve)
  ├─ Extras: install_extras (skip existentes)
  ├─ Brain: scripts sim, dados never
  └─ "Rode /init-engram se houver backup para merge"

/init-engram
  ├─ Se backup existe → Fase 0.5 (merge + cleanup)
  ├─ Fase 1–7 (análise, plano, agents, skills, knowledge, cérebro)
  └─ Brain do projeto nunca substituído
```

---

## 7. Tarefas de implementação (atualizadas)

| # | Tarefa | Tipo |
|---|--------|------|
| A1 | Alterar update: agents e seeds aditivos (não sobrescrever) | setup.sh |
| A2 | Remover /update-engram | core/commands/ |
| A3 | Inserir Fase 0.5 no init-engram (merge + cleanup) | init-engram.md |
| A4 | Corrigir verify_installation | setup.sh |
| B1 | prune_agents.py | core/genesis/scripts/ |
| B2 | analyze_project: customization, auth-expert, infra-expert | analyze_project.py |
| B3 | auth-expert, agent-customization-guide | extras/, core/genesis/references/ |
| B4 | Integrar Fase 2.5 Agents no init-engram | init-engram.md |
| C1 | (Backlog) Migração automática do brain | brain_sqlite.py |

---

## 8. Checklist pré-implementação

- [ ] Opção A (backup sempre) aprovada
- [ ] Update aditivo (A1) aprovado
- [ ] Brain migration deixada para backlog
- [ ] Ordem de tarefas aceita
- [ ] Iniciar por A1–A4, depois B1–B4
