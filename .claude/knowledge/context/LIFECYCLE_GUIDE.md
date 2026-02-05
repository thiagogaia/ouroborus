# Engram/Ouroboros — Guia do Ciclo de Vida Completo

> Documento gerado em 2026-02-05. Descreve o fluxo real de uso do sistema.

---

## Visao Geral

```
Instalar → Trabalhar → Aprender → Evoluir → Dormir → Repetir
   ↑                                                    |
   └────────────── cada sessao mais inteligente ←───────┘
```

---

## ATO 1: Instalacao (uma unica vez)

```bash
$ git clone git@github.com:meu-org/meu-projeto.git
$ cd meu-projeto
$ /init-engram
```

O `/init-engram` roda 7 fases automaticas:

1. **Analisa o projeto** — detecta stack (Next.js, Flask, NestJS, etc.)
2. **Gera knowledge files** — CURRENT_STATE.md, PATTERNS.md, ADR_LOG.md, DOMAIN.md, PRIORITY_MATRIX.md, EXPERIENCE_LIBRARY.md
3. **Gera skills** — baseado na stack detectada (ex: prisma-migration, api-testing)
4. **Gera agents** — subagentes especializados (ex: db-expert, frontend-reviewer)
5. **Gera commands** — /learn, /recall, /doctor, /create, etc.
6. **Popula o cerebro** — le commits, ADRs, patterns, regras de negocio → grafo
7. **Limpa templates** — remove scaffolds ja usados

**Resultado:** `.claude/` populado, cerebro com ~100-200 nos, CLAUDE.md com instrucoes.

---

## ATO 2: Inicio de Sessao

O dev abre o Claude Code e pede uma feature. O Claude automaticamente:

### Passo 1: Consulta o Cerebro (primario)
```
/recall "tema da tarefa"
```
Retorna nos relevantes COM conexoes semanticas:
- ADRs relacionados
- Bugs anteriores no mesmo escopo
- Regras de negocio aplicaveis
- Patterns aprovados

### Passo 2: Complementa com .md files (fallback)
```
CURRENT_STATE.md → onde o projeto esta agora
PRIORITY_MATRIX.md → prioridades atuais
PATTERNS.md → patterns a seguir
```

### Passo 3: Entende o contexto completo antes de codificar

---

## ATO 3: Trabalho na Feature

### Decisao Arquitetural
Se ha decisao a tomar:
- Consulta ADRs existentes via /recall
- Registra nova ADR antes de implementar

### Orquestracao Runtime
Se precisa de expertise nao coberta:
- Claude cria skill/agent sob demanda via engram-genesis
- Registra no manifest com `source=runtime`
- Maximo 2 componentes por sessao

### Implementacao
- Usa skills existentes
- Delega a agents especializados
- Segue patterns do PATTERNS.md

### Review
```
/review
```
Pipeline: correcao → padroes → seguranca → performance

---

## ATO 4: Commit

```
/commit
```
Gera mensagem semantica automatica baseada no diff.

---

## ATO 5: Aprendizado (/learn) — Final da Sessao

### Fase 1: Coleta
```bash
git diff --stat HEAD~5
git log --oneline -10
```

### Fase 2: Introspeccao
Claude reflete: patterns, decisoes, problemas, conhecimento de dominio.

### Fase 3: Atualizar Knowledge Files
- CURRENT_STATE.md → status atualizado
- PATTERNS.md → patterns novos
- ADR_LOG.md → decisoes registradas
- DOMAIN.md → regras de negocio
- EXPERIENCE_LIBRARY.md → experiencias reutilizaveis
- PRIORITY_MATRIX.md → tarefas atualizadas

### Fase 4: Alimentar o Cerebro

#### 4.1 Processar commits
```bash
python3 .claude/brain/populate.py commits 20
```

#### 4.2 Memorias episodicas (bugs, solucoes)
```python
brain.add_memory(title="Bug: ...", labels=["Episode", "BugFix"])
```

#### 4.3 Memorias conceituais (glossario)
```python
brain.add_memory(title="Conceito X", labels=["Concept", "Glossary"])
```

#### 4.4 Consolidacao leve
```bash
python3 .claude/brain/cognitive.py consolidate
```

#### 4.4b SONO — Consolidacao Semantica
```bash
python3 .claude/brain/sleep.py
```

5 fases do sono:

| Fase | Funcao |
|------|--------|
| **dedup** | Encontra e merge nos duplicados |
| **connect** | Descobre refs cruzadas (ADR-xxx, PAT-xxx, [[wikilinks]]), SAME_SCOPE, MODIFIES_SAME |
| **relate** | Cosine similarity entre embeddings → RELATED_TO |
| **themes** | Agrupa commits por scope → Theme nodes |
| **calibrate** | Ajusta pesos por frequencia de acesso |

**Resultado:** conexoes que nenhum humano escreveu. O sistema descobre sozinho que Bug X esta ligado ao ADR Y.

#### 4.5 Health Check
```bash
python3 .claude/brain/cognitive.py health
```

#### 4.6 Embeddings
```bash
python3 .claude/brain/embeddings.py build
```

### Fase 5: Evolucao
```bash
# Rastreia uso de skills
python3 register.py --activate --type skill --name [nome]

# Detecta co-ativacoes
python3 co_activation.py --log-session --skills [skill1],[skill2]

# Verifica componentes subutilizados
python3 track_usage.py --report stale
```

### Fase 6: Resumo ao Dev
Apresenta tudo que foi registrado + sugestoes evolutivas.

---

## ATO 6: Proxima Sessao

O Claude consulta o cerebro e **sabe tudo** da sessao anterior:
- Decisoes tomadas e seus trade-offs
- Bugs resolvidos e como foram resolvidos
- Regras de negocio descobertas
- Connections semanticas entre tudo isso

**Cada sessao comeca onde a anterior parou.**

---

## Relacao .md Files ↔ Cerebro

```
.md files  = FONTE (humano le e edita)
cerebro    = INDICE CONECTADO (maquina busca e navega)
```

### Fluxo de Dados

```
ADR_LOG.md ─────── populate_adrs() ──────→ ADR + Decision nodes
PATTERNS.md ────── populate_patterns() ──→ Pattern + ApprovedPattern nodes
DOMAIN.md ─────── populate_domain() ────→ Concept, BusinessRule, Glossary nodes
EXPERIENCE_LIB ── populate_experiences()→ Episode nodes
git log ────────── populate_commits() ──→ Commit + Episode nodes
                                              ↓
                                         sleep.py
                                              ↓
                                    Conexoes Semanticas
                                    (RELATED_TO, SAME_SCOPE,
                                     MODIFIES_SAME, REFERENCES,
                                     BELONGS_TO_THEME, CLUSTERED_IN)
```

### O que o cerebro ADICIONA que os .md NAO tem

| Capacidade | .md files | Cerebro |
|---|---|---|
| Leitura humana | Sim | Nao |
| Edicao direta | Sim | Via API |
| Busca por similaridade | Nao | Sim (embeddings) |
| Conexoes semanticas | Nao | Sim (sleep) |
| Travessia de grafo | Nao | Sim (spreading activation) |
| Pesos de relevancia | Nao | Sim (calibrate) |
| Performance em escala | Degrada | Constante (~200ms) |

### Quando os .md se tornam insuficientes

- **Ate ~100KB:** .md sao suficientes, cerebro e um bonus
- **100KB-1MB:** cerebro acelera buscas, .md ainda legivel
- **1MB+:** cerebro se torna essencial — ler .md inteiro e inviavel
- **10MB+:** sem cerebro, o sistema nao funciona eficientemente

### Regra de Ouro

> Os .md files sao a fonte canonica. O cerebro e o indice inteligente.
> Se apagar o cerebro: `populate.py all` recria tudo.
> Se apagar os .md: o cerebro fica orfao.

---

## Tipos de Aresta Semantica (criadas pelo Sono)

| Tipo | Significado | Exemplo |
|------|-------------|---------|
| REFERENCES | Ref cruzada explicita | ADR-015 cita [[RN-035]] |
| INFORMED_BY | Pattern informado por ADR | PAT-014 ← ADR-015 |
| APPLIES | Commit aplica Pattern | commit abc ← PAT-014 |
| RELATED_TO | Similaridade semantica | "JWT auth" ~ "2FA TOTP" |
| SAME_SCOPE | Mesmo scope de commit | feat(auth): X ~ feat(auth): Y |
| MODIFIES_SAME | Tocam mesmos arquivos | commit A e B ambos tocam auth.ts |
| BELONGS_TO_THEME | Commit pertence a Theme | commit → Theme:auth |
| CLUSTERED_IN | Pattern em cluster | PAT-014 → Cluster:security |

---

## Metricas de Saude

```bash
python3 .claude/brain/cognitive.py health
```

| Metrica | Peso | O que mede |
|---|---|---|
| Weak memory ratio | 30% | % de memorias fracas (peso < 0.3) |
| Semantic connectivity | 40% | % de nos com arestas semanticas |
| Embedding coverage | 30% | % de nos com embeddings |

| Score | Status | Acao |
|---|---|---|
| > 0.9 | healthy | Nenhuma |
| 0.7-0.9 | needs_attention | Rodar sleep.py |
| < 0.7 | critical | Rodar populate + sleep + embeddings build |
