# Architecture Decision Records
> Genesis-only: este arquivo é criado no setup e populado no /init-engram. Após isso, o cérebro é a fonte primária. Consulte: `python3 .claude/brain/recall.py "<tema>" --type ADR --top 10 --format json`
> Última atualização: 2026-02-06 (genesis-only desde ADR-020)

## ADR-001: Sistema Metacircular
**Data**: 2026-02-03
**Status**: ✅ Aceito
**Decisores**: Design inicial

### Contexto
Engram v1 tinha skills fixos. Adicionar novos exigia edição manual. Cada projeto tinha os mesmos skills, mesmo que a stack fosse diferente.

### Decisão
Implementar sistema metacircular onde genesis gera skills sob demanda baseado na stack detectada, e evolution rastreia uso para propor melhorias.

### Consequências
- ✅ Skills customizados por projeto
- ✅ Sistema se auto-evolui
- ✅ Menos manutenção manual
- ⚠️ Maior complexidade inicial
- ⚠️ Requer schemas bem definidos

---

## ADR-002: Skills com Frontmatter YAML
**Data**: 2026-02-03
**Status**: ✅ Aceito

### Contexto
Precisamos de metadados estruturados (name, description) para validação e registro, mas queremos manter markdown legível.

### Decisão
Usar frontmatter YAML (delimitado por ---) no início de SKILL.md. Body continua markdown puro.

### Alternativas Consideradas
1. ❌ JSON separado — dois arquivos, mais complexo
2. ❌ Tudo YAML — menos legível para humanos
3. ✅ Frontmatter YAML — padrão da indústria (Jekyll, Hugo, MDX)

### Consequências
- ✅ Validação automática via parse simples
- ✅ Legível por humanos
- ✅ Compatível com editores markdown
- ⚠️ Parser YAML básico (sem recursos avançados)

---

## ADR-003: Agents Não Invocam Outros Agents
**Data**: 2026-02-03
**Status**: ✅ Aceito

### Contexto
Task tool permite invocar subagents. Se agents pudessem invocar outros agents, poderíamos ter loops infinitos ou explosão de contexto.

### Decisão
Agents são terminais — podem usar tools (Read, Grep, etc) mas NUNCA Task. Orquestração fica com o Claude principal.

### Consequências
- ✅ Sem risco de loops infinitos
- ✅ Controle de contexto previsível
- ✅ Debug mais simples
- ⚠️ Composição requer skill intermediário

---

## ADR-004: Progressive Disclosure
**Data**: 2026-02-03
**Status**: ✅ Aceito

### Contexto
Carregar todos os skills no início desperdiça tokens e sobrecarrega o contexto.

### Decisão
Skills são carregados sob demanda quando o Claude detecta necessidade (via triggers na description) ou quando invocados explicitamente.

### Consequências
- ✅ Menor uso de tokens
- ✅ Contexto mais focado
- ✅ Escalável para muitos skills
- ⚠️ Descriptions devem ter triggers claros

---

## ADR-005: Python para Scripts Internos
**Data**: 2026-02-03
**Status**: ✅ Aceito

### Contexto
Scripts de genesis/evolution precisam manipular JSON, parsear markdown, validar estruturas.

### Decisão
Usar Python 3 sem dependências externas. Funciona em qualquer máquina com Python instalado.

### Alternativas Consideradas
1. ❌ Node.js — requer npm install
2. ❌ Bash puro — muito verboso para JSON/parsing
3. ✅ Python stdlib — universal, expressivo, sem deps

### Consequências
- ✅ Zero dependências
- ✅ Funciona em macOS, Linux, WSL
- ✅ Fácil de manter
- ⚠️ Requer Python 3.8+

---

## ADR-006: Manifest como Source of Truth
**Data**: 2026-02-03
**Status**: ✅ Aceito

### Contexto
Precisamos saber quais componentes existem, suas versões, uso, saúde.

### Decisão
manifest.json é o registro central. register.py mantém sincronizado. doctor.py detecta dessincronização.

### Consequências
- ✅ Single source of truth
- ✅ Métricas de uso automáticas
- ✅ Health tracking
- ⚠️ Precisa manter sincronizado

---

## ADR-007: Adoção do Engram (Bootstrap)
**Data**: 2026-02-03
**Status**: ✅ Aceito

### Contexto
Este projeto É o próprio Engram — um caso metacircular onde o sistema gerencia a si mesmo.

### Decisão
Usar Engram para desenvolver Engram, demonstrando o conceito de auto-alimentação (ouroboros).

### Consequências
- ✅ Dogfooding — usamos o que construímos
- ✅ Bugs encontrados mais rápido
- ✅ Demonstra viabilidade do sistema
- ⚠️ Bootstrap paradox (precisamos do sistema para melhorar o sistema)

---

## ADR-008: Arquitetura Git-Native com Grafo de Conhecimento
**Data**: 2026-02-03
**Status**: ✅ Aceito
**Decisores**: Análise de escalabilidade para multi-dev/multi-org

### Contexto

O Engram precisa escalar para:
- 10+ desenvolvedores por projeto
- 3-5 anos de uso contínuo
- ~25.000 episódios, ~125.000 eventos ao longo do tempo
- Múltiplas organizações usando o sistema

Problemas a resolver:
1. **Sync entre devs**: Como compartilhar conhecimento sem conflitos?
2. **Custo de tokens**: Claude não pode ler 25k arquivos (12.5M tokens = $37/sessão)
3. **Assertividade**: Como encontrar conhecimento relevante em massa de dados?
4. **Simplicidade**: Evitar infraestrutura cloud complexa

### Decisão

Adotar arquitetura **Git-native com grafo de conhecimento estilo Obsidian**:

#### 1. Git como Backend (não cloud custom)

```
.claude/ é Git-tracked e compartilhada entre todos os devs
Git fornece: sync, histórico, review (PR), rollback, blame
Zero infraestrutura adicional
```

#### 2. Estrutura de Arquivos Escalável

```
.claude/
├── active/              ← HOT (sempre carregado, ~90 dias)
│   ├── state/           ← 1 arquivo POR DEV (nunca conflita)
│   ├── episodes/        ← 1 arquivo por episódio
│   ├── patterns/        ← 1 arquivo por pattern
│   ├── decisions/       ← 1 arquivo por ADR
│   ├── concepts/        ← glossário linkável [[conceito]]
│   └── people/          ← quem sabe o quê [[@pessoa]]
│
├── consolidated/        ← WARM (summaries trimestrais)
│   └── YYYY-QN.md       ← 50 episódios → 1 resumo
│
├── archive/             ← COLD (busca sob demanda)
│   └── YYYY/QN/         ← episódios originais > 90 dias
│
├── graph/               ← GRAFO UNIFICADO (substitui index/)
│   ├── backlinks.json   ← fonte de verdade (grafo + metadados + views)
│   └── embeddings.db    ← opcional, busca semântica
│
└── scripts/             ← AUTOMAÇÃO
    ├── build_graph.py   ← gera backlinks.json
    ├── consolidate.py   ← compacta episódios antigos
    └── search.py        ← busca no grafo
```

**Nota**: INDEX.md foi eliminado. O grafo (backlinks.json) com `views` pré-computadas
serve como índice. Se necessário para humanos, INDEX.md pode ser gerado do grafo.

#### 3. Links Estilo Obsidian (Grafo Emergente)

Todos os arquivos usam [[wikilinks]] para criar conexões:

```markdown
# Bug de Refresh Token

**Autor**: [[@joao]]
**Tags**: #auth #bug #jwt

Seguindo [[ADR-002-jwt]], o [[refresh-token]] não invalidava.
Resolvi com [[Redis]] usando pattern [[token-blacklist]].
Ver também: [[2024-01-15-maria-auth-setup]]
```

Convenções:
- `[[@pessoa]]` → people/pessoa.md
- `[[ADR-NNN]]` → decisions/ADR-NNN.md
- `[[conceito]]` → concepts/conceito.md
- `[[pattern-name]]` → patterns/pattern-name.md

#### 4. Grafo Unificado (backlinks.json)

O grafo substitui índices separados. Um único `graph/backlinks.json` contém:

```json
{
  "meta": {
    "generated_at": "2026-02-03T17:00:00",
    "total_nodes": 342,
    "total_edges": 1247
  },
  "nodes": {
    "2024-02-03-joao-refresh-bug": {
      "path": "active/episodes/...",
      "type": "episode",
      "author": "@joao",
      "date": "2024-02-03",
      "tags": ["auth", "bug"],
      "title": "Bug de Refresh Token"
    }
  },
  "edges": [...],
  "backlinks": {
    "ADR-002-jwt": ["episode-1", "episode-2", "pattern-x"]
  },
  "views": {
    "recent_episodes": ["...", "..."],
    "hubs": [{"id": "autenticação", "connections": 67}],
    "clusters": {"auth": ["jwt", "@maria", "ADR-002"]},
    "team_state": {"@joao": {"focus": "auth"}}
  }
}
```

**O grafo É o índice.** INDEX.md eliminado (ou gerado opcionalmente para humanos).

#### 5. Estratégia de Escalabilidade

| Camada | Conteúdo | Tokens | Quando Carrega |
|--------|----------|--------|----------------|
| backlinks.json | Grafo completo | ~3-5k | Sempre (início) |
| state/*.md | Contexto por dev | ~500/dev | Sempre |
| active/* | Últimos 90 dias | Sob demanda | Navegação por [[link]] |
| consolidated/* | Summaries | Sob demanda | Busca profunda |
| archive/* | Originais antigos | Sob demanda | grep encontra |

**Fluxo de navegação**:
1. Claude recebe backlinks.json (sabe o que existe + conexões)
2. Identifica nós relevantes pelos metadados e hubs
3. Lê arquivos específicos seguindo [[links]]
4. Backlinks mostram impacto de mudanças
5. Custo: ~$0.15/sessão (grafo mais eficiente que índice texto)

#### 6. Consolidation (Job Mensal)

```python
# consolidate.py
# Episódios > 90 dias → summaries trimestrais
# Originais movidos para archive/
# INDEX.md atualizado
```

### Alternativas Consideradas

1. ❌ **Cloud custom (API + PostgreSQL)**
   - Complexidade alta
   - Custo de infraestrutura
   - Vendor lock-in
   - Não funciona offline

2. ❌ **.claude/ por desenvolvedor (não compartilhado)**
   - Conhecimento não flui entre devs
   - Cada um reinventa a roda
   - Perde valor de memória coletiva

3. ❌ **Arquivo monolítico (um grande KNOWLEDGE.md)**
   - Conflitos de merge constantes
   - Não escala (arquivo gigante)
   - Difícil buscar

4. ✅ **Git-native + arquivos granulares + grafo de links**
   - Zero infraestrutura
   - Merge automático (arquivos diferentes)
   - Grafo emerge dos links
   - Escala com consolidation
   - Funciona offline

### Consequências

**Benefícios:**
- ✅ Zero custo de infraestrutura (Git já existe)
- ✅ Funciona 100% offline
- ✅ Histórico completo grátis (git log)
- ✅ Review de conhecimento via PR
- ✅ Rollback grátis (git revert)
- ✅ Escala para 10+ devs, 5+ anos
- ✅ Tokens sob controle (~$0.20/sessão)
- ✅ Grafo de conhecimento emerge naturalmente
- ✅ Backlinks identificam especialistas e impacto

**Trade-offs:**
- ⚠️ Requer disciplina de [[links]] nos arquivos
- ⚠️ Tags obrigatórias em episódios
- ⚠️ Job de consolidation deve rodar mensalmente
- ⚠️ build_graph.py deve rodar após mudanças (ou no /learn)
- ⚠️ Conflitos possíveis em concepts/ (raro, resolvível)

**Métricas de Sucesso:**
- Custo/sessão < $0.50
- Merge conflicts < 5% dos PRs
- Tempo de busca < 5s
- Onboarding de dev novo < 1 semana

### Referências

- Obsidian: https://obsidian.md (modelo de links)
- Zettelkasten: método de notas interconectadas
- Git como database: https://git-scm.com

---

## ADR-009: Estado Por Desenvolvedor
**Data**: 2026-02-03
**Status**: ✅ Aceito
**Relacionado**: [[ADR-008]]

### Contexto

Com múltiplos devs trabalhando no mesmo projeto, o arquivo de estado (CURRENT_STATE.md) conflitaria constantemente.

### Decisão

Cada dev tem seu próprio arquivo de estado:

```
.claude/active/state/
├── joao.md       ← contexto do @joao
├── maria.md      ← contexto da @maria
└── _team.md      ← GERADO (merge de todos)
```

- Dev edita só seu arquivo → nunca conflita
- `_team.md` é gerado por script → nunca editado manualmente
- Script roda no /status ou /learn

### Consequências

- ✅ Zero conflitos de merge em estado
- ✅ Cada dev tem contexto personalizado
- ✅ _team.md dá visão geral da equipe
- ⚠️ Precisa identificar dev (identity.json ou git config)

---

## ADR-010: Commits de Conhecimento
**Data**: 2026-02-03
**Status**: ✅ Aceito
**Relacionado**: [[ADR-008]]

### Contexto

Precisamos de convenção para commits que modificam .claude/ para facilitar histórico e blame.

### Decisão

Usar prefixo `knowledge(@autor):` para commits de conhecimento:

```
knowledge(@joao): auth bug resolution session
knowledge(@maria): new billing patterns discovered
decision(@team): ADR-008 approved - git-native architecture
pattern(@pedro): add circuit-breaker pattern
episode(@joao): production incident post-mortem
```

### Consequências

- ✅ Fácil filtrar: `git log --grep="knowledge(@joao)"`
- ✅ Blame mostra quem contribuiu conhecimento
- ✅ Consistente com conventional commits
- ⚠️ Requer disciplina da equipe

---

## ADR-011: Arquitetura de Cérebro Organizacional
**Data**: 2026-02-03
**Status**: ✅ Aceito
**Relacionado**: [[ADR-008]], [[ADR-009]]

### Contexto

O Engram precisa de um sistema de memória que funcione como um cérebro organizacional real:
- Memória episódica (experiências), semântica (conceitos), procedural (patterns)
- Consolidação (fortalecer memórias importantes)
- Esquecimento (decay de memórias não acessadas)
- Busca semântica (por significado, não só texto)
- Grafo de conhecimento (relações tipadas entre conceitos)

Escala alvo: dezenas de desenvolvedores trabalhando por anos.

### Decisão

Implementar arquitetura híbrida:

#### 1. Storage em Camadas

```
.claude/
├── brain/                    ← GRAFO E ÍNDICES
│   ├── graph.json           ← Nós e arestas (NetworkX serializado)
│   ├── embeddings.npz       ← Vetores semânticos (numpy)
│   └── state/               ← Estado por desenvolvedor
│       └── @{username}.json
│
├── memory/                   ← CONTEÚDO LEGÍVEL (Markdown)
│   ├── episodes/            ← Memória episódica
│   ├── concepts/            ← Memória semântica
│   ├── patterns/            ← Memória procedural
│   ├── decisions/           ← ADRs
│   ├── people/              ← Expertise por pessoa
│   └── domains/             ← Áreas de conhecimento
│
├── consolidated/             ← MEMÓRIAS COMPACTADAS
│   └── {YYYY-QN}-summary.md
│
└── archive/                  ← MEMÓRIAS ARQUIVADAS
    └── {YYYY}/
```

#### 2. Estrutura de Nós

```json
{
  "id": "uuid",
  "labels": ["Episode", "BugFix", "AuthDomain"],
  "props": {
    "title": "...",
    "author": "@joao",
    "content_path": "memory/episodes/uuid.md",
    "summary": "..."
  },
  "memory": {
    "strength": 0.85,
    "access_count": 12,
    "last_accessed": "2024-02-10",
    "decay_rate": 0.01
  }
}
```

#### 3. Tipos de Relações (Arestas)

| Tipo | Descrição |
|------|-----------|
| AUTHORED_BY | Pessoa criou o nó |
| REFERENCES | Menção explícita |
| SOLVED_BY | Problema resolvido por pattern/decisão |
| CAUSED_BY | Causalidade |
| BELONGS_TO | Pertence a domínio |
| SUPERSEDES | Nova versão substitui antiga |
| SIMILAR_TO | Similaridade semântica (auto-detectado) |

#### 4. Processos Cognitivos

| Processo | Frequência | Função |
|----------|------------|--------|
| Encode | Cada /learn | Criar memória, gerar embedding, criar arestas |
| Retrieve | Cada busca | Spreading activation + similaridade |
| Consolidate | Semanal | Fortalecer conexões, detectar patterns |
| Decay | Diário | Aplicar curva de esquecimento |

#### 5. Stack Técnica

- **Grafo em memória**: NetworkX (Python)
- **Persistência**: JSON (Git-friendly)
- **Embeddings**: numpy + sentence-transformers (local) ou OpenAI
- **Busca vetorial**: Bruta para <100k, FAISS/Annoy para mais

### Alternativas Consideradas

1. ❌ **Neo4j** — Muito pesado (JVM), não Git-friendly
2. ❌ **SQLite com tabelas** — JOINs lentos para travessia de grafo
3. ❌ **Só arquivos Markdown** — Sem grafo real, busca limitada
4. ✅ **NetworkX + JSON + embeddings** — Leve, Git-friendly, grafo real

### Consequências

**Benefícios:**
- ✅ Grafo real com travessia O(1) em memória
- ✅ Git-friendly (JSON é texto, embeddings usa LFS)
- ✅ Busca semântica por significado
- ✅ Memórias decaem naturalmente (menos ruído)
- ✅ Spreading activation encontra conhecimento relacionado
- ✅ Escala para ~1M nós confortavelmente
- ✅ Dependência leve (só NetworkX e numpy)

**Trade-offs:**
- ⚠️ Precisa carregar grafo em memória (~200MB para 50k nós)
- ⚠️ Embeddings requerem regeneração se mudar modelo
- ⚠️ Merge de graph.json pode conflitar (resolver com rebuild)
- ⚠️ LFS necessário para embeddings.npz em repos grandes

**Métricas de Sucesso:**
- Tempo de carregamento < 2s
- Busca com spreading activation < 100ms
- Memórias relevantes no top 10 > 80% das vezes
- Decay remove >50% de ruído após 90 dias

---

## ADR-000: Inspiração Arquitetural (Voyager + DGM + BOSS)
**Data**: 2026-02-03 (commit bbcc8777 - inicial)
**Status**: ✅ Aceito
**Decisores**: Design inicial baseado em pesquisa de mercado

### Contexto

Antes de criar o Engram v2, foi realizada pesquisa de soluções de mercado para sistemas auto-alimentados. Três projetos se destacaram como inspiração arquitetural:

1. **Voyager (NVIDIA/MineDojo)**: Agente de Minecraft que constrói sua própria biblioteca de skills à medida que explora. Skills simples compõem skills complexos.

2. **Darwin Gödel Machine (Sakana AI)**: Agente que reescreve seu próprio código-fonte. Mantém arquivo evolutivo de todas as versões.

3. **BOSS (Bootstrap Your Own Skills - USC/Google)**: Bootstrapping bottom-up de skills através de prática. Skills emergem de padrões detectados.

### Decisão

Combinar as melhores ideias de cada projeto:

| Projeto | Conceito Adotado | Implementação no Engram |
|---------|------------------|-------------------------|
| Voyager | Skill Library composicional | `composes:` em SKILL.md + co_activation.py |
| Voyager | Verificação antes de commit | validate.py obrigatório |
| DGM | Arquivo evolutivo | .claude/versions/ + archive.py |
| DGM | Sistema modifica a si mesmo | engram-genesis pode gerar si mesmo |
| BOSS | Skill emergente de padrão | /learn detecta padrões → propõe skill |
| BOSS | Composição bottom-up | co_activation.py → sugere composite |

### Alternativas Consideradas

1. ❌ **Copiar Voyager exatamente** — Requer ambiente de testes (jogo), não aplicável a dev
2. ❌ **Apenas DGM** — Muito agressivo (reescreve código arbitrariamente)
3. ✅ **Síntese das três abordagens** — Combina pontos fortes, evita complexidade

### Consequências

- ✅ Fundação conceitual sólida baseada em pesquisa
- ✅ Cada feature tem justificativa acadêmica
- ✅ Roadmap claro derivado de gaps identificados
- ⚠️ Algumas features (curriculum automático) ainda não implementadas
- ⚠️ Experiential replay ainda não integrado

### Referências

- Voyager Paper: https://arxiv.org/abs/2305.16291
- DGM Paper: Sakana AI (2024)
- BOSS Paper: USC/Google (NeurIPS 2023)
- Documento completo: `Engram_self_bootstrap_analysis.md`

---

## ADR-012: Separação setup.sh e batch-setup.sh
**Data**: 2026-02-04 (commit bbcf725)
**Status**: ✅ Aceito
**Relacionado**: [[PAT-033]]

### Contexto

O setup.sh acumulou funcionalidade de batch (múltiplos diretórios, `--batch` flag, progress indicator, summary) que aumentou o arquivo em +175 linhas (783 → 958) e misturou lógica de loop com lógica de instalação.

### Decisão

Reverter setup.sh para versão single-project e criar batch-setup.sh como wrapper que chama setup.sh em loop.

### Alternativas Consideradas

1. ❌ **Manter tudo no setup.sh** — Feature creep, viola single responsibility
2. ❌ **Revert sem batch** — Perde funcionalidade útil para CI/CD
3. ✅ **Separar em dois scripts** — Cada arquivo faz uma coisa bem feita

### Consequências

- ✅ setup.sh voltou a ser simples e focado (783 linhas)
- ✅ batch-setup.sh é independente e descartável (177 linhas)
- ✅ Unix philosophy restaurada
- ⚠️ Dois arquivos para manter ao invés de um

---

## Template para Novas Decisões

```markdown
## ADR-013: Remoção de Componentes Órfãos (Ciclo Ouroboros)
**Data**: 2026-02-05
**Status**: ✅ Aceito
**Relacionado**: [[ADR-001]] (Sistema Metacircular), [[PAT-034]]

### Contexto
Análise da ANALISE_IMPLEMENTA.md revelou que 3 componentes não participavam do ciclo ouroboros:
- `execution-pipeline`: duplicava /plan→/review→/commit→/learn, assumia Docker obrigatório
- `microservices-navigator`: fora do escopo local (análise cross-repo), overlap de 40% com base-ingester
- `SERVICE_MAP.md.tmpl`: nenhum skill, command ou workflow o lia ou atualizava

### Decisão
Remover os 3 componentes. O Engram é local e metaprogramável — usuários criam skills sob demanda com `/create` se precisarem de pipeline rígido ou navegação de microserviços.

### Alternativas Consideradas
1. ❌ Reenquadrar execution-pipeline como task-planner — ainda duplicaria /plan
2. ❌ Reescrever microservices-navigator como complementar ao ingester — foge do escopo local
3. ✅ Remover — o sistema já cobre os casos de uso via componentes existentes + /create sob demanda

### Consequências
- ✅ Menos peso morto em extras/ (362 linhas removidas)
- ✅ Princípio claro: componente sem consumidor = remover
- ✅ Reforça filosofia de geração sob demanda vs pré-fabricação
- ⚠️ Usuários que esperavam esses extras precisam criar via /create

---

## ADR-014: Ciclo de Sono para Consolidação Semântica
**Data**: 2026-02-05
**Status**: ✅ Aceito
**Relacionado**: [[ADR-011]] (Arquitetura de Cérebro), [[PAT-012]] (Venv Isolado)

### Contexto
O cérebro tinha 151 nós e 234 arestas, mas 100% eram estruturais (AUTHORED_BY + BELONGS_TO). Zero conexões semânticas. Era uma cópia dos .md sem inteligência — topologia estrela onde tudo apontava para person-engram e domain-X.

Causas raiz: IDs uuid4 causavam duplicatas, `_resolve_link()` nunca encontrava nós por prop/prefixo, populate.py nunca passava `references=`, e o venv com numpy/networkx existia mas nenhum script o ativava.

### Decisão
Implementar ciclo de sono (`sleep.py`) inspirado no sono biológico com 5 fases:
1. **dedup** — merge nós duplicados (IDs determinísticos md5)
2. **connect** — refs cruzadas (ADR/PAT/EXP/wikilinks, same_scope, modifies_same)
3. **relate** — similaridade vetorial (embeddings ou TF fallback)
4. **themes** — agrupa commits por scope, patterns por domínio
5. **calibrate** — ajusta pesos por acesso

Auto-ativação do venv via `site.addsitedir()` no brain.py para que numpy/networkx estejam sempre disponíveis.

### Alternativas Consideradas
1. ❌ Forçar refs manuais no populate — não escala, depende de parse perfeito
2. ❌ Embedding-only — requer modelo pesado, não funciona sem GPU
3. ✅ 5 fases complementares — funciona com ou sem embeddings, incremental

### Consequências
- ✅ De 0 para 68 arestas semânticas (REFERENCES, SAME_SCOPE, MODIFIES_SAME, RELATED_TO, BELONGS_TO_THEME, CLUSTERED_IN)
- ✅ 134 duplicatas removidas na primeira execução
- ✅ health_score de 0.47 para 0.75 (40% do score agora mede conectividade semântica)
- ✅ /recall mostra conexões — spreading activation navega rede rica
- ✅ Idempotente — rodar sleep múltiplas vezes não cria duplicatas
- ⚠️ relate() com TF vectors é impreciso para textos curtos (threshold 0.75 ajuda)

---

## ADR-NNN: Título
**Data**: YYYY-MM-DD
**Status**: 🟡 Proposto | ✅ Aceito | ❌ Rejeitado | ⚠️ Superseded
**Relacionado**: [[ADR-XXX]] (se aplicável)

### Contexto
[Qual problema estamos resolvendo?]

### Decisão
[O que decidimos fazer?]

### Alternativas Consideradas
1. ❌ Alternativa A — [motivo rejeição]
2. ❌ Alternativa B — [motivo rejeição]
3. ✅ Escolhida — [motivo escolha]

### Consequências
- ✅ Benefício 1
- ✅ Benefício 2
- ⚠️ Trade-off 1
```

## ADR-015: Brain-Primary Architecture with Synced .md Files
**Data**: 2026-02-05
**Status**: Aceito
**Contexto**: A arquitetura brain-only tratava o cérebro como fonte única de verdade e os .md de knowledge como legado. Risco: fallback fica stale se .md não são atualizados.
**Decisão**: Adotar brain-primary — cérebro é fonte primária para busca/conexões, .md de knowledge mantidos em sincronia como espelho legível (PATTERNS.md, ADR_LOG.md, DOMAIN.md, EXPERIENCE_LIBRARY.md). Boot files (CURRENT_STATE.md, PRIORITY_MATRIX.md) sempre atualizados.
**Consequências**:
- ✅ /learn atualiza cérebro E .md na mesma fase
- ✅ Fallback real (não stale), git diffs mostram evolução
- ✅ Conhecimento acessível sem Python
- ⚠️ Dual-write — dois lugares para manter em sincronia

## ADR-016: Rewrite do_update() with 8 Gap Fixes and Safety Invariants
**Data**: 2026-02-06
**Status**: ✅ Aceito
**Contexto**: do_update() original era cópia rasa de install_core() com 8 gaps: sem brain scripts, sem backup, sem comparação de versão, sem manifest update, seeds sobrescritos sem aviso, CLAUDE.md/settings.json não preservados.
**Decisão**: Reescrever com 13 passos, 2 helpers (backup_for_update, update_manifest_json), 2 flags (--force, --regenerate). Invariantes: graph.json/embeddings.npz/\*.jsonl NUNCA sobrescritos, knowledge NUNCA tocado, manifest entries NUNCA removidas, backup timestampado sempre criado.
**Consequências**:
- ✅ Updates seguros e reversíveis
- ✅ VERSION como fonte da verdade (source vs local)
- ✅ batch-setup.sh usa --force em vez de pipe hack
- ✅ --regenerate para recriar configs com backup

## ADR-017: SQLite Schema v2 — Hybrid Property Graph with Generated Columns
**Data**: 2026-02-06
**Status**: ✅ Aceito
**Contexto**: Schema v1 do brain.db tinha 4 defeitos: PRIMARY KEY(src,tgt) impedia multi-edge, labels como JSON array sem índice, duas fontes de verdade (props_json + colunas), 16 json.loads() em Python.
**Decisão**: Redesenhar como hybrid property graph: `properties JSON` como fonte única com `GENERATED ALWAYS AS (json_extract(...)) STORED` columns, `node_labels` table normalizada, `UNIQUE(from_id, to_id, type)` para multi-edge, `json_set()` para reinforce atômico.
**Consequências**:
- ✅ Multi-edge funciona: 5 novas MODIFIES_SAME entre pares com SAME_SCOPE existente
- ✅ Labels indexadas: O(1) lookup via idx_labels_label
- ✅ Uma fonte de verdade: impossível inconsistência props vs colunas
- ✅ 195/195 testes passam sem mudança (testam JSON backend)
- ✅ Health 0.97, 212 nós, 524+ arestas migradas sem perda
- ✅ Rollback: BRAIN_BACKEND=json + graph.json exportado

## ADR-018: CURRENT_STATE.md Genesis-Only
**Data**: 2026-02-06
**Status**: ✅ Aceito
**Contexto**: CURRENT_STATE.md consumia ~4500 tokens/sessão e crescia indefinidamente. Toda informação já existia no cérebro (timestamps, commits, estado).
**Decisão**: CURRENT_STATE.md é criado apenas no genesis (setup.sh + /init-engram primeira vez). Após isso, o cérebro é a fonte primária via recall temporal (--recent 7d). 30+ arquivos editados para remover referências ativas.
**Consequências**:
- ✅ Economia de ~4500 tokens/sessão
- ✅ CURRENT_STATE.md fica como snapshot histórico no git
- ✅ Cérebro usa temporal query para "onde estávamos?"
- ⚠️ Requer temporal recall funcional (implementado em ADR-019)

## ADR-019: Temporal Recall via since/sort_by
**Data**: 2026-02-06
**Status**: ✅ Aceito
**Contexto**: brain_sqlite.py retrieve() ignorava timestamps (created_at, last_accessed) apesar de existirem no schema v2. Não era possível fazer queries temporais.
**Decisão**: Adicionar `since` (ISO date ou relativo '7d'/'24h') e `sort_by` ('score'|'date') ao retrieve(). Helpers: `_resolve_since()`, `_created_after()`, `_sort_by_date()`. recall.py ganha `--recent`, `--since`, `--sort` flags.
**Consequências**:
- ✅ Substitui leitura de CURRENT_STATE.md
- ✅ 11 novos testes (206 total)
- ✅ Fix numpy truth value bug (not array → is None)
- ✅ Fix JSON output corrompido por print() em stdout
