Inicializar o Engram para este projeto usando o sistema de auto-geração.

**Este comando cria tudo do zero.** Se houver backup, fará merge e cleanup antes de prosseguir.

## Fase 0.5: Merge do Backup (quando backup existe)

1. Execute a detecção:
```bash
python3 .claude/skills/engram-genesis/scripts/migrate_backup.py --project-dir . --detect --output json
```

2. Se `found: true`, executar merge em vez de alertar:
   - **agents, skills, commands, knowledge, settings**: merge conforme análise (migrate_backup)
   - **brain**: NUNCA tocar — manter o brain do projeto

3. Executar análise e merge:
```bash
python3 .claude/skills/engram-genesis/scripts/migrate_backup.py --project-dir . --analyze --output json
python3 .claude/skills/engram-genesis/scripts/migrate_backup.py --project-dir . --migrate --strategy smart
```

4. Após merge confirmado, cleanup:
```bash
python3 .claude/skills/engram-genesis/scripts/migrate_backup.py --project-dir . --cleanup
```

5. Prosseguir para Fase 1.

Se `found: false`, prosseguir diretamente para Fase 1.

## Fase 1: Análise do Projeto

1. Execute o analisador de projeto:
```bash
python3 .claude/skills/engram-genesis/scripts/analyze_project.py --project-dir . --output json
```

2. Leia o resultado e entenda a stack detectada e sugestões de componentes.

## Fase 2: Apresentar Plano

Apresente ao dev o plano de geração ANTES de executar:

```
🐍 Engram Init — Plano de Geração
═══════════════════════════════════

Stack detectada: [listar]

Skills a gerar:
  🔴 [nome] — [razão]
  🟡 [nome] — [razão]

Agents:
  Remover: [to_remove]
  Manter e customizar: [to_keep]
  Criar e customizar: [to_create]

Seeds universais (já instalados):
  ✅ project-analyzer
  ✅ knowledge-manager
  ✅ domain-expert
  ✅ priority-engine
  ✅ code-reviewer

[Se houve merge na Fase 0.5:]
Migrados do backup:
  ✅ [componentes preservados]

Continuar? (perguntar ao dev)
```

## Fase 2.5: Agents — Prune, Create, Customize

**Só agents.** A Fase 3 trata skills.

1. Calcular: needed = [a["name"] for a in suggestions["agents"]], existing = agents em `.claude/agents/*.md`, to_remove = existing - needed, to_keep = existing ∩ needed, to_create = needed - existing
2. **Prune**: `python3 .claude/skills/engram-genesis/scripts/prune_agents.py --project-dir . --needed agent1,agent2,... --output json` (lista = needed comma-separated)
3. **Create**: Para cada em to_create: `python3 .claude/skills/engram-genesis/scripts/generate_component.py --type agent --name X --project-dir .` (scaffold)
4. **Customize**: Para cada em (to_keep ∪ to_create), Claude customiza usando `.claude/skills/engram-genesis/references/agent-customization-guide.md` e output do analyze_project (suggestions.agents[i].customization)
5. **Validar**: `python3 .claude/skills/engram-genesis/scripts/validate.py --type agent --path .claude/agents/{name}.md`
6. **Registrar**: `python3 .claude/skills/engram-genesis/scripts/register.py --type agent --name {name} --project-dir .`

## Fase 3: Auto-Geração via Genesis — Skills

Ativar o skill `engram-genesis`. Para cada **skill** aprovado:

1. Gerar scaffold via `generate_component.py`
2. **Customizar o conteúdo** para este projeto específico (workflow, padrões da stack)
3. Validar via `validate.py`
4. Registrar via `register.py`

## Fase 4: Popular Knowledge

Preencher knowledge files com dados reais:

### CURRENT_STATE.md + Cérebro (população inicial)
A análise profunda vai para **ambos** — é a única vez que CURRENT_STATE.md é populado:
- Analisar o codebase em profundidade
- Mapear módulos, dependências, estado de cada área
- Identificar dívidas técnicas
- Listar bloqueios conhecidos

**Escrever no CURRENT_STATE.md** (snapshot legível para git e leitura humana):
- Status geral, fase, saúde, stack, bloqueios, próximo marco

**Registrar no cérebro** via `brain.add_memory()` (fonte primária a partir daqui):
```python
import sys
sys.path.insert(0, '.claude/brain')
from brain_sqlite import BrainSQLite as Brain

brain = Brain()
brain.load()
dev = {"author": "@engram"}  # ou get_current_developer() se disponível

# Estado inicial do projeto
brain.add_memory(
    title="Estado Inicial: [nome do projeto]",
    content="## Status\n[fase, saúde, stack]\n\n## Módulos\n[...]\n\n## Dívidas Técnicas\n[...]\n\n## Bloqueios\n[...]",
    labels=["State", "Genesis"],
    author=dev["author"],
    props={"phase": "genesis", "date": "[YYYY-MM-DD]"}
)

brain.save()
```

**Nota**: após o genesis, CURRENT_STATE.md não é mais atualizado — o cérebro assume via recall temporal (`--recent 7d`)

### PATTERNS.md
- Inspecionar código existente
- Detectar padrões recorrentes (naming, estrutura, error handling)
- Registrar como padrões aprovados

### DOMAIN.md
- Analisar nomes de entidades, variáveis, tabelas
- Extrair glossário do domínio
- Mapear regras de negócio implícitas no código

### PRIORITY_MATRIX.md
- Buscar TODOs no código
- Identificar issues/bugs óbvios
- Priorizar com ICE Score

### EXPERIENCE_LIBRARY.md
- Criar vazia (será populada pelo /learn)

## Fase 5: Popular Cérebro Organizacional

O cérebro em `.claude/brain/` deve ser populado com conhecimento existente.

### 5.1 Verificar venv do Brain
```bash
# Verifica se venv existe e ativa
if [[ -d ".claude/brain/.venv" ]]; then
    source .claude/brain/.venv/bin/activate
fi
```

### 5.2 Popular com conhecimento existente

Processar ADRs, conceitos de domínio, patterns e commits:
```bash
.claude/brain/.venv/bin/python3 .claude/brain/populate.py all
```

Isso irá:
- Extrair ADRs do ADR_LOG.md
- Extrair conceitos do DOMAIN.md (glossário, regras, entidades)
- Extrair patterns do PATTERNS.md
- Processar últimos 7000 commits do git (memória episódica)
- **Ingerir estrutura do código via AST** (módulos, classes, funções)
- **Enriquecer commits com diff** (símbolos modificados)

### 5.3 Gerar Embeddings para Busca Semântica
```bash
.claude/brain/.venv/bin/python3 .claude/brain/embeddings.py build
```

Usa ChromaDB HNSW como vector store (instalado pelo setup.sh). Modelo local: `all-MiniLM-L6-v2` (384 dims).

### 5.4 Verificar Saúde do Cérebro
```bash
.claude/brain/.venv/bin/python3 .claude/brain/cognitive.py health
```

Se `status: healthy`, continuar. Se não, seguir recomendações.
Se `vector_backend: npz`, reinstalar deps: `source .claude/brain/.venv/bin/activate && pip install chromadb pydantic-settings`

### 5.5 Reportar ao Dev
```
🧠 Cérebro Organizacional Populado
══════════════════════════════════

Memórias criadas:
  📋 [X] ADRs (decisões arquiteturais)
  📚 [Y] Conceitos (glossário + regras)
  🔄 [Z] Patterns (padrões aprovados)
  📝 [W] Commits (memória episódica)

Total: [N] nós, [M] arestas
Grau médio: [G] (conectividade)
Embeddings: [E] vetores gerados
Vector store: [chromadb | npz]

Status: 🟢 Saudável
```

---

## Fase 6: Health Check

Executar `/doctor` para validar a instalação completa.

## Fase 7: Cleanup e Relatório Final

1. Remover staging de templates (se existir):
```bash
rm -rf .claude/templates/
```

2. **Atualizar CLAUDE.md com seção Cérebro Organizacional** (após o cérebro estar populado):

   - Verificar se `CLAUDE.md` já contém `## Cérebro Organizacional`. Se sim, pular.
   - Se não contiver:
     1. Ler o conteúdo de `.claude/skills/engram-genesis/references/claude_cerebro_section.md`
     2. Inserir essa seção **após** `## Orquestração Inteligente` e **antes** de `## Regras de Ouro`
     3. Atualizar o bloco "Antes de Codificar" para incluir item 3 "Saúde do cérebro" e a frase "O cérebro é a **fonte primária e única**. O recall retorna conteúdo completo (campo `content`) e suporta **busca temporal** (`--recent Nd`, `--since YYYY-MM-DD`, `--sort date`). Os `.md` de knowledge são mantidos em sincronia como fallback."
     4. Atualizar a Nota para: "Todo conhecimento novo (decisões, padrões, experiências, conceitos) vai via `brain.add_memory()` — o cérebro é a única entrada. O recall é a forma de consultar. Único .md editável: `.claude/knowledge/priorities/PRIORITY_MATRIX.md`."

3. Apresentar resumo do que foi:
   - Gerado (novos componentes)
   - Migrado (do backup)
   - Populado (knowledge files)
   - Validado (health check)
   - CLAUDE.md atualizado com seção Cérebro (se aplicável)

4. Sugerir próximos passos concretos baseado nas prioridades detectadas.

```
🐍 Engram Init — Concluído!
═══════════════════════════════════

✅ Componentes gerados: X skills, Y agents
✅ Migrados do backup: Z items
✅ Knowledge populado: 6 arquivos
✅ Cérebro populado: N nós, M arestas, E embeddings
✅ CLAUDE.md atualizado com seção Cérebro Organizacional (cérebro como fonte da verdade)
✅ Health check: PASSED

🗑️  Backups removidos (migração concluída)

Próximos passos sugeridos:
  1. [baseado em PRIORITY_MATRIX]
  2. [baseado em PRIORITY_MATRIX]
  3. [baseado em PRIORITY_MATRIX]

Use /status para ver o estado atual.
Use /learn após cada sessão para retroalimentar.
Use .claude/brain/maintain.sh health para ver saúde do cérebro.
```
