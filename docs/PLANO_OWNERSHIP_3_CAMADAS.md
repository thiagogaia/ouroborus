# Plano: Modelo de Ownership em 3 Camadas para core/ vs .claude/

## Contexto

O Engram tem `core/` como distribuição e `.claude/` como instância instalada. O projeto instalou em si mesmo (`setup.sh .`), e a instância evoluiu durante sessões de trabalho. Melhorias universais foram feitas em `.claude/` mas nunca propagadas de volta ao `core/`. Resultado: drift bidirecional — nem `core/` nem `.claude/` estão 100% corretos.

O `setup.sh --update` sobrescreve commands sem cerimônia, destruindo melhorias feitas em `.claude/`. Não existe mecanismo de detecção de drift nem classificação formal de quem é dono de cada arquivo.

## Modelo de 3 Camadas

| Camada | Source of truth | Comportamento no update | Exemplos |
|--------|----------------|------------------------|----------|
| **CORE-OWNED** | `core/` | SOBRESCREVE sempre | commands, dna, genesis, evolution, seeds |
| **PROJECT-OWNED** | `.claude/` | NUNCA sobrescreve | agents, skills gerados, knowledge, CLAUDE.md |
| **RUNTIME** | gerado em uso | Nunca no core | brain.db, manifest.json, *.jsonl, .venv |

## Implementação em 6 Steps

### Step 1: Sync one-time — propagar melhorias de .claude/ para core/

Dois padrões de drift encontrados:

**A) Path expansion PRIORITY_MATRIX.md** — `.claude/` expandiu refs para path completo, `core/` ficou com bare ref. Arquivos a corrigir em `core/`:

| Arquivo | Linhas | De → Para |
|---------|--------|-----------|
| `core/commands/plan.md` | 42 | `PRIORITY_MATRIX.md` → `.claude/knowledge/priorities/PRIORITY_MATRIX.md` |
| `core/commands/priorities.md` | 20 | idem |
| `core/dna/knowledge.schema.md` | 39 | idem |
| `core/seeds/domain-expert/SKILL.md` | 53 | idem |
| `core/seeds/knowledge-manager/SKILL.md` | 29, 40, 41, 44 | idem |
| `core/seeds/priority-engine/SKILL.md` | 6, 35, 41, 49 | idem |
| `core/genesis/SKILL.md` | 95 | idem |

**B) Doctor brain health section** — `.claude/commands/doctor.md` ganhou seção "Saúde do Cérebro" (12 linhas). Adicionar ao `core/commands/doctor.md`.

**C) Python path em .claude/** — Alguns arquivos em `.claude/` regrediram de `.venv/bin/python3` para `python3` (plan.md, priorities.md). Estes serão corrigidos automaticamente quando `setup.sh --update .` copiar do `core/` (que já está correto).

### Step 2: Criar `sync-check.sh`

Script bash (~120 linhas) na raiz do repo que:

- **`./sync-check.sh`** — reporta drift entre `core/` e `.claude/` para arquivos Layer 1
- **`./sync-check.sh --sync core`** — copia `.claude/` → `core/` com confirmação por arquivo
- **`./sync-check.sh --sync project`** — copia `core/` → `.claude/` (update targeted)
- **`./sync-check.sh --quiet`** — exit code 0=ok, 1=drift (para scripting)

Mapeamentos Layer 1 cobertos:
- `core/commands/*.md` ↔ `.claude/commands/*.md`
- `core/dna/*.md` ↔ `.claude/dna/*.md`
- `core/genesis/SKILL.md` ↔ `.claude/skills/engram-genesis/SKILL.md`
- `core/genesis/scripts/*.py` ↔ `.claude/skills/engram-genesis/scripts/*.py`
- `core/genesis/references/*` ↔ `.claude/skills/engram-genesis/references/*`
- `core/evolution/SKILL.md` ↔ `.claude/skills/engram-evolution/SKILL.md`
- `core/evolution/scripts/*.py` ↔ `.claude/skills/engram-evolution/scripts/*.py`
- `core/seeds/*/SKILL.md` ↔ `.claude/skills/*/SKILL.md` (somente seeds que existem em ambos)

### Step 3: Adicionar drift warning no `setup.sh --update`

No `do_update()`, antes da linha 910 (`cp core/commands/*.md`), inserir bloco que:
1. Compara cada command de `core/` vs `.claude/`
2. Se drift detectado, lista os arquivos e avisa que serão sobrescritos
3. Sugere rodar `./sync-check.sh --sync core` antes
4. Pede confirmação (bypass com `--force`)

~25 linhas adicionadas no `setup.sh`.

### Step 4: Criar documentação `core/OWNERSHIP.md`

Documento autoritativo (~60 linhas) que classifica cada diretório/arquivo nas 3 camadas. Serve como referência para desenvolvedores e como especificação para o sync-check.

### Step 5: Propagar core/ corrigido para .claude/

Rodar `setup.sh --update .` no próprio repo para que as correções do Step 1 fluam de `core/` → `.claude/`. Isso corrige automaticamente os python paths regressados e adiciona a seção doctor ao .claude/.

### Step 6: Validação final

- `./sync-check.sh` → zero drift
- `diff core/commands/ .claude/commands/` → zero diff (todos os 16 commands)
- `git diff --stat` → confirmar que só arquivos esperados mudaram

## Arquivos a criar

| Arquivo | Tipo | Linhas |
|---------|------|--------|
| `sync-check.sh` | Bash script | ~120 |
| `core/OWNERSHIP.md` | Documentação | ~60 |

## Arquivos a modificar

| Arquivo | Natureza da mudança |
|---------|--------------------|
| `core/commands/doctor.md` | +12 linhas: seção "Saúde do Cérebro" |
| `core/commands/plan.md` | 1 path expansion |
| `core/commands/priorities.md` | 1 path expansion |
| `core/dna/knowledge.schema.md` | 1 path expansion |
| `core/seeds/domain-expert/SKILL.md` | 1 path expansion |
| `core/seeds/knowledge-manager/SKILL.md` | 4 path expansions |
| `core/seeds/priority-engine/SKILL.md` | 4 path expansions |
| `core/genesis/SKILL.md` | 1 path expansion |
| `setup.sh` | +25 linhas: drift warning no do_update() |
| `CHANGELOG.md` | Documentar mudanças |

## Verificação

1. `./sync-check.sh` retorna exit 0 (zero drift)
2. `diff -rq core/commands/ .claude/commands/` sem diferenças
3. `setup.sh --update .` roda sem warnings de drift
4. Simular drift manual (editar `.claude/commands/status.md`) → `./sync-check.sh` detecta → `./sync-check.sh --sync core` resolve

## Commits planejados

1. `fix(core): propagate .claude/ improvements back to core (path expansions + doctor health section)`
2. `feat: add sync-check.sh for drift detection between core/ and .claude/`
3. `feat(setup): add pre-update drift warning for core-owned files`
4. `docs: add three-layer ownership model (core/OWNERSHIP.md)`
5. `chore: sync .claude/ from corrected core/ via update`
