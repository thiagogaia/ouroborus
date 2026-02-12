---
name: base-ingester
description: Ingestão em massa de documentação externa no cérebro organizacional.
  Use quando precisar absorver uma base de conhecimento inteira (diretório de
  markdowns) de uma vez, em vez de registrar incrementalmente via /learn. Parseia
  markdown estruturado, extrai entidades, cria nós tipados e arestas automáticas
  no grafo, e regenera embeddings.
---

# Base Ingester

Ingestão bulk de bases de conhecimento externas no cérebro do Engram.

## Quando Usar

- Absorver documentação de projeto existente (wikis, READMEs, runbooks)
- Importar base de conhecimento de domínio (regras de negócio, glossários)
- Carregar mapeamento de serviços/microserviços
- Importar documentação de infraestrutura

## Workflow

### 1. Preparar a Base

A base deve ser um diretório com arquivos `.md`. Estrutura livre, mas quanto
mais organizada, melhor a ingestão:

```
base/
├── arquitetura-macro.md      # Visão geral
├── fluxos-negocio.md         # Regras e entidades
├── services.md               # Mapa de serviços
├── infra.md                  # Infra overview
├── services/                 # Detalhes por serviço
│   ├── service-a.md
│   └── service-b.md
└── infra/                    # Detalhes de infra
    ├── kubernetes.md
    └── ci-cd.md
```

### 2. Executar Ingestão

```bash
python3 .claude/skills/base-ingester/scripts/ingest.py \
  --source /path/to/base \
  --project-dir . \
  --type domain
```

Parâmetros:
- `--source`: Caminho do diretório com os `.md` (obrigatório)
- `--project-dir`: Raiz do projeto com Engram instalado (default: `.`)
- `--type`: Tipo de base — `domain`, `infra`, `services`, `mixed` (default: `mixed`)
- `--dry-run`: Mostra o que seria criado sem executar
- `--author`: Autor das memórias (default: detecta via git)

### 3. Verificar Resultado

```bash
# Estatísticas do cérebro
python3 .claude/brain/brain.py stats

# Buscar algo ingerido
python3 .claude/brain/recall.py "nome do serviço"
```

### 4. Regenerar Embeddings

A ingestão NÃO gera embeddings automaticamente (performance).
Após ingerir, regenere:

```bash
python3 .claude/brain/embeddings.py build
```

## O Que o Script Extrai

### De cada arquivo `.md`:
- **Título** (H1) → nome do nó
- **Descrição** (primeiro parágrafo) → summary
- **Conteúdo completo** → salvo em `memory/`

### De tabelas:
- Tabelas com colunas `Serviço/Service` → nós tipo `Service`
- Tabelas com colunas `Endpoint/Rota/Route` → nós tipo `Endpoint`
- Tabelas com colunas `Entidade/Entity` → nós tipo `Entity`

### Relações automáticas:
- Referências entre arquivos → `REFERENCES`
- Serviços mencionados em outros → `DEPENDS_ON`
- Entidades dentro de contextos → `BELONGS_TO`
- Hierarquias (sub-headers) → `CONTAINS`

## Tipos de Base

| Tipo | Labels padrão | Decay rate | Uso |
|------|---------------|------------|-----|
| `domain` | Concept, Rule, Entity | 0.003 | Regras de negócio, glossários |
| `infra` | Concept, Pattern | 0.005 | Infra, DevOps, CI/CD |
| `services` | Service, Concept | 0.003 | Mapeamento de microserviços |
| `mixed` | Concept | 0.005 | Base genérica |

## Regras

- NUNCA ingerir sem informar ao dev quantos nós/arestas serão criados (use --dry-run)
- SEMPRE verificar se a base não duplica conhecimento já existente no cérebro
- SEMPRE regenerar embeddings após ingestão
- Se a base tem > 100 arquivos, sugerir ingestão por subdiretório
- Ingestão é idempotente: rodar duas vezes não duplica (usa hash do conteúdo)
