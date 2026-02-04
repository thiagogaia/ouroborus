Ingerir base de conhecimento externa no cérebro organizacional.

O dev vai fornecer um caminho para um diretório com arquivos `.md`.

## Workflow

### 1. Validar Input

O argumento é o caminho para o diretório fonte. Se não fornecido, pergunte.

Aceitar também tipo opcional: `domain`, `infra`, `services`, `mixed` (default: `mixed`).

Exemplos de invocação:
- `/ingest ~/docs/base`
- `/ingest ~/docs/base --type domain`
- `/ingest ~/docs/base --type services`

### 2. Dry Run Primeiro

SEMPRE rodar dry-run antes de ingerir:

```bash
python3 .claude/skills/base-ingester/scripts/ingest.py \
  --source <PATH> \
  --project-dir . \
  --type <TYPE> \
  --dry-run
```

Mostrar ao dev:
- Quantos arquivos serão processados
- Quantos nós e arestas serão criados
- Quais serviços/entidades foram detectados
- Se há duplicatas que serão puladas

### 3. Confirmar e Executar

Após aprovação do dev, executar sem `--dry-run`:

```bash
python3 .claude/skills/base-ingester/scripts/ingest.py \
  --source <PATH> \
  --project-dir . \
  --type <TYPE>
```

### 4. Regenerar Embeddings

Após ingestão, regenerar embeddings:

```bash
python3 .claude/brain/embeddings.py build
```

### 5. Verificar

Rodar uma busca para confirmar:

```bash
python3 .claude/brain/brain.py stats
```

Informar ao dev o resultado final.

## Regras

- SEMPRE rodar dry-run antes da ingestão real
- SEMPRE pedir confirmação do dev após dry-run
- SEMPRE regenerar embeddings após ingestão
- Se > 100 arquivos, sugerir ingerir por subdiretório
- Informar se houver duplicatas puladas
