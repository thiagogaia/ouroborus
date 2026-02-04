# Brain - Cerebro Organizacional

Sistema de memoria com grafo de conhecimento, embeddings e processos cognitivos.

## Estrutura

```
brain/
├── brain.py          # Nucleo do cerebro (grafo + operacoes)
├── embeddings.py     # Geracao de embeddings para busca semantica
├── cognitive.py      # Processos: consolidate, decay, archive
├── graph.json        # Grafo serializado (nos + arestas)
├── embeddings.npz    # Vetores de embedding
└── state/            # Estado por desenvolvedor
    └── @username.json
```

## Dependencias

```bash
# Minimo (grafo funciona)
pip install networkx

# Para busca semantica local (gratis)
pip install sentence-transformers numpy

# OU para OpenAI embeddings (melhor, pago)
pip install openai numpy
export OPENAI_API_KEY=sk-...
```

## Uso Basico

### Python

```python
from brain import Brain

# Carrega cerebro
brain = Brain()
brain.load()

# Adiciona memoria
node_id = brain.add_memory(
    title="Bug de autenticacao",
    content="Refresh token nao invalidava apos logout...",
    labels=["Episode", "BugFix"],
    author="@joao"
)

# Busca
results = brain.retrieve(query="problemas de autenticacao")
for r in results:
    print(f"{r['score']:.2f} - {r['props']['title']}")

# Salva
brain.save()
```

### CLI

```bash
# Estatisticas
python brain.py stats

# Busca por texto
python brain.py search "autenticacao"

# Adicionar memoria rapida
python brain.py add "Titulo" "Conteudo da memoria"

# Consolidacao (rodar semanalmente)
python cognitive.py consolidate

# Decay (rodar diariamente)
python cognitive.py decay

# Saude do cerebro
python cognitive.py health

# Gerar embeddings
python embeddings.py build

# Busca semantica
python embeddings.py search "como resolver bugs de auth"
```

## Conceitos

### Labels (Tipos de Memoria)

| Label | Tipo | Decay Rate |
|-------|------|------------|
| Episode | Memoria episodica | 0.01 (medio) |
| Concept | Memoria semantica | 0.003 (lento) |
| Pattern | Memoria procedural | 0.005 (lento) |
| Decision | ADR | 0.001 (muito lento) |
| Person | Membro da equipe | 0.0001 (quase nao decai) |
| Domain | Area de conhecimento | 0.0001 |

### Tipos de Arestas

| Tipo | Significado |
|------|-------------|
| AUTHORED_BY | Pessoa criou a memoria |
| REFERENCES | Mencao explicita ([[link]]) |
| BELONGS_TO | Pertence a dominio |
| SOLVED_BY | Problema resolvido por pattern/decisao |
| SUPERSEDES | Nova versao substitui antiga |
| SIMILAR_TO | Similaridade semantica (auto-detectado) |

### Processos Cognitivos

1. **Encode**: Criar memoria com arestas automaticas
2. **Retrieve**: Busca com spreading activation
3. **Consolidate**: Fortalecer conexoes (semanal)
4. **Decay**: Esquecimento por Ebbinghaus (diario)
5. **Archive**: Mover memorias fracas (quando necessario)

## Integracao com Git

```bash
# Adiciona arquivos do cerebro
git add .claude/brain/graph.json
git add .claude/memory/

# Para embeddings grandes, use LFS
git lfs track "*.npz"
git add .claude/brain/embeddings.npz

# Commit
git commit -m "knowledge(@joao): session about auth bugs"
```

## Processos Cognitivos Periodicos

Para manter o cerebro saudavel, configure jobs periodicos:

### Opcao 1: Git Hooks (Recomendado)

Adicione ao `.git/hooks/post-commit`:

```bash
#!/bin/bash
# Roda decay a cada commit (leve, ~100ms)
cd "$(git rev-parse --show-toplevel)"
python3 .claude/brain/cognitive.py decay 2>/dev/null || true
```

### Opcao 2: Cron (Para times maiores)

```bash
# Editar crontab
crontab -e

# Adicionar:
# Decay diario (2am)
0 2 * * * cd /path/to/projeto && python3 .claude/brain/cognitive.py decay && git add .claude/brain/graph.json && git commit -m "chore(brain): daily decay" --no-verify 2>/dev/null || true

# Consolidacao semanal (domingo 3am)
0 3 * * 0 cd /path/to/projeto && python3 .claude/brain/cognitive.py consolidate && git add .claude/brain/graph.json && git commit -m "chore(brain): weekly consolidation" --no-verify 2>/dev/null || true

# Archive mensal (dia 1, 4am)
0 4 1 * * cd /path/to/projeto && python3 .claude/brain/cognitive.py archive && git add .claude/brain/ .claude/archive/ && git commit -m "chore(brain): monthly archive" --no-verify 2>/dev/null || true
```

### Opcao 3: CI/CD

Adicione ao seu pipeline (GitHub Actions exemplo):

```yaml
# .github/workflows/brain-maintenance.yml
name: Brain Maintenance
on:
  schedule:
    - cron: '0 2 * * *'  # Diario 2am UTC
  workflow_dispatch:

jobs:
  decay:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install networkx
      - run: python .claude/brain/cognitive.py decay
      - run: python .claude/brain/cognitive.py health
      - uses: stefanzweifel/git-auto-commit-action@v5
        with:
          commit_message: "chore(brain): automated decay"
          file_pattern: ".claude/brain/graph.json"
```

### Verificacao Manual

```bash
# Ver saude do cerebro
python3 .claude/brain/cognitive.py health

# Ver log de processos
cat .claude/brain/cognitive-log.jsonl | tail -5

# Forcar consolidacao
python3 .claude/brain/cognitive.py consolidate
```

## Escala

| Metrica | Limite Confortavel |
|---------|-------------------|
| Nos | ~1M |
| Arestas | ~5M |
| Embeddings | ~100k |
| RAM | ~500MB |
| Tempo de carga | <2s |
