# Análise: Fluxo de Update e Paths do generate_component

> Pontos: 1) auth-expert em extras, 2) fluxo de update (backup, /update-engram), 3) paths no projeto alvo.

---

## 1. auth-expert → extras

**Decisão**: Criar `extras/agents/auth-expert.md`. O setup (via install_extras) instala em `.claude/agents/`. Sem mover arquivos.

---

## 2. Fluxo de Update — Análise

### 2.1 Situação atual

| Fluxo | Backup | Nome |
|-------|--------|------|
| **Install** (já existe config) | Sim | `.claude.bak/`, `CLAUDE.md.bak` |
| **Update** (setup --update) | Sim | `.claude.update-backup.{timestamp}/` |

O `migrate_backup.py` só detecta `.claude.bak/` e `CLAUDE.md.bak`. Não vê `.claude.update-backup.*`.

### 2.2 Unificar backup para simplificar

**Proposta**: Update usar os mesmos nomes do install:
- `.claude/` → `.claude.bak/`
- `CLAUDE.md` → `CLAUDE.md.bak`

Assim o `migrate_backup` continua funcionando sem mudar. O fluxo fica:

1. Backup: cp .claude → .claude.bak, cp CLAUDE.md → CLAUDE.md.bak
2. Sobrescrever .claude com conteúdo novo

### 2.3 Fluxo de update — simples

```
1. Criar backups (.claude.bak/, CLAUDE.md.bak)
2. Sobrescrever .claude/ e CLAUDE.md com versão nova
```

Quem faz isso hoje: `setup.sh --update` (no repositório Engram, com acesso a core, extras, etc.).

### 2.4 /update-engram vs init-engram

**init-engram hoje**:
- Fase 0: migrate_backup (detecta .claude.bak, analisa, migra)
- Fase 1–7: análise, geração, popular knowledge, cérebro, etc.

**/update-engram como comando**:
- Poderia concentrar a lógica de “após update”: migrar do backup, aplicar decisões (prune/customize agents).
- init-engram voltaria a focar em inicialização nova.

**Opções**:

| Opção | Descrição |
|-------|-----------|
| **A** | Manter tudo no init-engram. Fase 0 detecta backup e migra. Sem /update-engram. |
| **B** | Criar /update-engram: migrar backup + prune/customize agents. init-engram sem Fase 0, ou Fase 0 enxuta que só redireciona. |
| **C** | /update-engram só para migração. init-engram continua com Fase 0, mas após update o usuário roda /update-engram primeiro. |

**Recomendação**: **Opção A** por enquanto — fluxo simples, init-engram continua único ponto de entrada. Se a Fase 0 ficar pesada, extrair para /update-engram depois.

**Fluxo ideal**:
1. `setup.sh --update` (no repo): backup + sobrescrever
2. `/init-engram` (no projeto): detecta backup, migra, faz prune/customize

### 2.5 Ajustes no setup.sh --update — ✅ Implementado

- Trocar `.claude.update-backup.{timestamp}` por `.claude.bak`
- Fazer backup de `CLAUDE.md` em `CLAUDE.md.bak` se existir
- Reaproveitar o mesmo padrão do install para consistência

---

## 3. Paths do generate_component — Projeto alvo

O projeto alvo **não tem** acesso ao repositório Engram. Só tem o que foi copiado para `.claude/`:

```
projeto_alvo/
├── .claude/
│   ├── agents/          ← core + extras (architect, db-expert, infra-expert, auth-expert, etc.)
│   ├── skills/
│   │   ├── engram-genesis/
│   │   │   ├── scripts/   ← generate_component.py vive aqui
│   │   │   ├── references/
│   │   └── ...
```

### 3.1 Onde buscar base para criar agent?

Quando `generate_component --type agent --name X` roda e X **não existe** em `.claude/agents/`:

| Origem | Disponível no projeto? |
|--------|-------------------------|
| `core/agents/` | Não (core não existe no projeto) |
| `extras/agents/` | Não (extras não existe no projeto) |
| `agent-bases/` | Não (core não terá agent-bases) |

**Solução**: Scaffold genérico. Claude customiza com inteligência (analyze_project, agent-customization-guide).

### 3.2 Decisão: sem agent-bases

O **core não terá** pasta `agent-bases`. Claude/Cursor cria agents com inteligência. O generate_component usa **apenas scaffold** quando o agent não existe. A customização é feita pelo Claude com base em analyze_project, agent-customization-guide e conhecimento do projeto.

**auth-expert**: **somente** em `extras/agents/auth-expert.md`. Nunca em core/agents.

---

## 4. Resumo de decisões

| Ponto | Decisão |
|-------|---------|
| auth-expert | `extras/agents/auth-expert.md` (somente extras) |
| agent-bases | Não criar. Scaffold + customização por Claude. |
| /update-engram | Criar comando separado — viável e recomendado |
