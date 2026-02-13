# DNA — Funcionamento Detalhado e Proposta de Melhorias

> Análise profunda do subsistema DNA: como funciona, quem consome, o que valida, e o que falta.

---

## 1. O Que É o DNA

O DNA é o **contrato formal** do Engram. Define a estrutura obrigatória de skills, agents, commands e knowledge files. Está em `core/dna/` e é copiado para `.claude/dna/` em cada projeto durante o `setup.sh`.

| Arquivo | Componente | Função |
|---------|------------|--------|
| `skill.schema.md` | Skills | Estrutura de diretório, frontmatter, body |
| `agent.schema.md` | Agents | Arquivo .md, frontmatter, body |
| `command.schema.md` | Commands | Arquivo .md sem frontmatter |
| `knowledge.schema.md` | Knowledge files | Estrutura de pastas, formato de cada arquivo |

---

## 2. Fluxo de Uso do DNA

```
┌─────────────────────────────────────────────────────────────────────────┐
│  FONTE                                                                   │
│  core/dna/*.schema.md                                                    │
│  (documentação + contrato)                                                │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                    setup.sh        │
                    cp -r core/dna → .claude/dna
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  CONSUMIDORES                                                            │
│                                                                          │
│  1. Genesis SKILL.md — Claude lê os .md ao gerar componentes           │
│     "Consultar Schema" → ler .claude/dna/skill.schema.md                 │
│                                                                          │
│  2. validate.py — Implementa as regras (NÃO lê os .md)                  │
│     Regras hardcoded; valida contra o contrato implícito                  │
│                                                                          │
│  3. generate_component.py — Gera scaffolds (NÃO lê os .md)             │
│     Estrutura genérica; não valida contra schema                         │
└─────────────────────────────────────────────────────────────────────────┘
```

** ponto importante:** O `validate.py` não lê os arquivos de schema. As regras estão duplicadas: no .md (documentação) e no código (validação). Qualquer mudança no schema exige atualizar ambos.

---

## 3. Regras por Schema vs Implementação no validate.py

### 3.1 Skill Schema

| Regra | Schema | validate.py | Status |
|-------|--------|-------------|--------|
| 1. SKILL.md existe | ✅ | ✅ | OK |
| 2. Frontmatter com name + description | ✅ | ✅ | OK |
| 3. name kebab-case e = nome do dir | ✅ | ✅ (warning se diff) | OK |
| 4. description 50–500 chars | ✅ | ✅ | OK |
| 5. Body ≤ 500 linhas | ✅ | ✅ (warning) | OK |
| 6. Scripts referenciados existem | ✅ | ⚠️ Parcial | Só verifica scripts/; não valida referências no body |
| 7. Scripts: shebang + executável | ✅ | ✅ | OK |
| 8. composes: skills existem | ✅ | ❌ | **Não implementado** — comenta "can't validate existence here" |
| 9. Sem README, CHANGELOG, etc. | ✅ | ✅ | OK |
| **description deve ter trigger** | ✅ ("Use quando...") | ❌ | **Não implementado** |
| **version** (opcional) | ✅ | ❌ | Não valida formato semver |

### 3.2 Agent Schema

| Regra | Schema | validate.py | Status |
|-------|--------|-------------|--------|
| 1. Arquivo .md em .claude/agents/ | ✅ | ✅ (recebe path) | OK |
| 2. Frontmatter: name, description, tools | ✅ | ✅ | OK |
| 3. name kebab-case = nome do arquivo | ✅ | ✅ | OK |
| 4. tools ⊆ settings.json | ✅ | ❌ | **Não implementado** |
| 5. skills: referenciados existem | ✅ | ❌ | **Não implementado** |
| 6. Body tem seção Regras | ✅ | ⚠️ Fraco | Só busca "regra" ou "rule" no texto |
| 7. Agent não invoca outro agent | ✅ | ❌ | Não verificável automaticamente |
| 8. Body ≤ 300 linhas | ✅ | ✅ | OK |
| **description 50–500 chars** | ✅ | ⚠️ | Só verifica min 50, não max 500 |

### 3.3 Command Schema

| Regra | Schema | validate.py | Status |
|-------|--------|-------------|--------|
| 1. Arquivo .md em .claude/commands/ | ✅ | ✅ | OK |
| 2. Nome kebab-case | ✅ | ❌ | Não valida nome do arquivo |
| 3. Conteúdo = instruções executáveis | ✅ | ⚠️ | Usa len < 20 como proxy grosseiro |
| 4. Pelo menos uma ação concreta | ✅ | ❌ | Não verifica steps numerados, etc. |
| 5. Pode referenciar skills, agents | ✅ | — | N/A |
| 6. Sem frontmatter | ✅ | ✅ | OK |
| 7. ≤ 200 linhas | ✅ | ✅ | OK |

### 3.4 Knowledge Schema

| Aspecto | Schema | validate.py | Status |
|---------|--------|-------------|--------|
| Estrutura | ✅ | ❌ | **Não há validate para knowledge** |
| Formato de entradas | ✅ | — | N/A |

O knowledge não tem validador. O schema existe como documentação; Genesis e populate usam heurísticas.

---

## 4. parse_frontmatter — Limitações

O `parse_frontmatter` em validate.py é um parser YAML simplificado.

### 4.1 O Que Funciona

- Frontmatter com `---`
- Chaves com valores simples
- Listas no formato `key:\n  - a\n  - b`
- Listas inline `key: [a, b]`

### 4.2 O Que Não Funciona

| Caso | Exemplo | Resultado |
|------|---------|-----------|
| **Descrição multiline** | `description: linha1\n  linha2` | Só `linha1` é capturada |
| **Valor com `:`** | `description: Use quando: X` | `val` pode ser cortado em `partition(":")` |
| **Lista com itens complexos** | `tools:\n  - Read\n  - Write` | OK |
| **YAML real** | `description: "texto com \"aspas\""` | Pode falhar |

A maioria dos skills usa description em múltiplas linhas. O parser ignora a continuação, mas como a primeira linha costuma ter 50+ caracteres, a validação passa. Um skill com description curta na primeira linha e longa na segunda falharia de forma incorreta.

---

## 5. Compatibilidade Python

O validate.py usa anotação `tuple[dict | None, str]`, que requer **Python 3.10+**. Em ambientes com Python 3.9 ou anterior, o script falha ao carregar:

```
TypeError: unsupported operand type(s) for |: 'type' and 'NoneType'
```

O projeto não declara versão mínima de Python; outros scripts do Genesis/Evolution podem ter o mesmo problema.

---

## 6. Onde o DNA É Usado

| Local | Uso |
|-------|-----|
| `setup.sh` | Copia core/dna/ → .claude/dna/ |
| `core/genesis/SKILL.md` | Instrui Claude a ler schemas ao gerar |
| `core/genesis/scripts/validate.py` | Implementa regras (sem ler os .md) |
| `core/genesis/scripts/generate_component.py` | Não usa schema |
| `core/commands/init-engram.md` | Não referencia DNA diretamente |
| `core/evolution/scripts/doctor.py` | Validação inline, não usa validate.py |

---

## 7. Avaliação: Está Funcionando?

### Funcionando

- Schemas documentados e coerentes
- Estrutura de skill, agent e command bem definida
- kebab-case e frontmatter coerentes
- validate cobre a maior parte das regras críticas
- Fluxo setup → .claude/dna → Genesis consulta

### Com Problemas

| Problema | Severidade | Impacto |
|----------|------------|---------|
| validate.py quebra em Python &lt; 3.10 | Alta | Instalação falha em muitos ambientes |
| composes: não valida existência | Média | Skill pode referenciar skill inexistente |
| agent tools vs settings.json | Média | Agent pode pedir permissão não permitida |
| agent skills: não valida existência | Média | Agent pode referenciar skill inexistente |
| description multiline truncada | Baixa | Descrições longas podem ser cortadas |
| description sem trigger | Baixa | Schema pede; validate não verifica |
| command sem validação de nome | Baixa | Arquivo command-foo.md pode ser inválido |
| knowledge sem validador | Baixa | Formato dos .md não é validado |

---

## 8. Propostas de Melhoria

### 8.1 Prioridade Alta

| # | Melhoria | Ação |
|---|----------|------|
| H1 | **Compatibilidade Python 3.9** | Trocar `dict \| None` por `Optional[dict]` ou `Union[dict, None]` |
| H2 | **validate composes** | Adicionar `--project-dir`; validar que composes apontam para skills existentes |

### 8.2 Prioridade Média

| # | Melhoria | Ação |
|---|----------|------|
| M1 | **validate agent tools** | Com `--project-dir`, ler settings.json e checar tools ⊆ allow |
| M2 | **validate agent skills** | Com `--project-dir`, checar que skills: existem em .claude/skills/ |
| M3 | **parse_frontmatter multiline** | Suportar continuação YAML para description (linhas que continuam valor sem `:` e sem `- `) |
| M4 | **command filename** | Validar que o nome do arquivo é kebab-case |

### 8.3 Prioridade Baixa

| # | Melhoria | Ação |
|---|----------|------|
| L1 | **description trigger** | Warning se description não contiver "Use quando" ou similar |
| L2 | **version semver** | Se version existir, validar padrão semver |
| L3 | **agent description max 500** | Adicionar validação de que description não excede 500 chars |
| L4 | **knowledge validator** | Script opcional para validar estrutura e formato dos knowledge files |

### 8.4 Opcional (Arquitetural)

| # | Melhoria | Ação |
|---|----------|------|
| A1 | **Schema como fonte única** | Validator ler os .md e extrair regras (mais complexo, exige parser de schema) |
| A2 | **Testes para validate** | Suite em tests/ para validate.py cobrindo regras e edge cases |

---

## 9. Resumo Executivo

| Aspecto | Status |
|---------|--------|
| **Documentação (schemas)** | ✅ Boa |
| **Cobertura no validate** | ⚠️ 70–80% |
| **Compatibilidade** | ❌ Python 3.10+ apenas |
| **Cross-references** | ❌ composes, agent skills não validados |
| **Parsing YAML** | ⚠️ Multiline não suportado |

**Conclusão:** O DNA está bem definido e usável, mas:

1. O validate precisa de ajuste urgente para Python 3.9.
2. As validações de cross-reference (composes, agent skills) agregam valor e dependem de `--project-dir`.
3. O parser de frontmatter pode ser melhorado para descrições multiline.
