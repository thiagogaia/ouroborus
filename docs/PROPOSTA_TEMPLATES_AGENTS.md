# Proposta: templates/agents/ para .claude/ Completo por Projeto

> Análise da ideia de adicionar agent templates e fazer init-engram gerar agents como skills.

---

## 1. Visão

O que falta seria **agents em templates**. O init-engram passaria a:

1. Verificar quais agents o projeto precisa
2. Usar templates quando existirem
3. Customizar para o projeto

Assim, `.claude/` seria criado com skills e agents específicos para cada projeto.

---

## 2. Estado Atual

### Skills (fluxo ok)

| Etapa | O que acontece |
|-------|----------------|
| setup | Copia `templates/skills/` → `.claude/templates/skills/` (staging) |
| init-engram | `analyze_project` sugere skills por stack |
| init-engram | `generate_component --type skill` busca template (ex: nextjs-patterns.skill.tmpl) |
| init-engram | Usa template ou scaffold, customiza |

### Agents (fluxo incompleto)

| Etapa | O que acontece |
|-------|----------------|
| setup | Copia `core/agents/*.md` → `.claude/agents/` (arquivos finais) |
| init-engram | `analyze_project` sugere agents (db-expert, architect, domain-analyst) |
| init-engram | `generate_component --type agent` encontra arquivo existente → não faz nada |
| init-engram | Nenhuma customização por projeto |

Os agents chegam prontos no setup; o init-engram não gera nem customiza.

---

## 3. Gaps

| # | Gap | Impacto |
|---|-----|---------|
| 1 | **Não existe templates/agents/** | Agents não seguem o fluxo de templates |
| 2 | **setup copia agents finais** | Init-engram não participa da criação de agents |
| 3 | **generate_agent não usa templates** | Sempre scaffold genérico |
| 4 | **Agents não são customizados por projeto** | Mesmo db-expert para Prisma e Drizzle |

---

## 4. Proposta: templates/agents/ e Fluxo Unificado

### 4.1 Nova estrutura

```
templates/
├── knowledge/     # (existente)
├── skills/        # (existente)
└── agents/       # NOVO
    ├── architect.agent.tmpl
    ├── db-expert.agent.tmpl
    ├── domain-analyst.agent.tmpl
    ├── db-expert-prisma.agent.tmpl    # quando orm=prisma
    ├── db-expert-drizzle.agent.tmpl   # quando orm=drizzle
    └── auth-expert-nextauth.agent.tmpl # quando auth=nextauth (opcional)
```

### 4.2 Duas abordagens possíveis

#### Abordagem A: Agents inteiramente via init-engram

| Etapa | Mudança |
|-------|---------|
| setup | Copia `templates/agents/` → `.claude/templates/agents/` |
| setup | **Não** copia mais `core/agents/` para `.claude/agents/` |
| init-engram | Para cada agent sugerido, `generate_component` usa template ou scaffold |
| init-engram | Customiza para o projeto |

**Efeito:** `.claude/agents/` fica vazio após o setup e é preenchido só pelo init-engram.

**Requisito:** Migrar conteúdo de `core/agents/` para `templates/agents/` (por ex. `architect.agent.tmpl`).

#### Abordagem B: Setup mantém base, templates adicionam variantes

| Etapa | Mudança |
|-------|---------|
| setup | Continua copiando `core/agents/` (3 universais) |
| setup | Copia `templates/agents/` → `.claude/templates/agents/` |
| init-engram | Para agents já existentes: customiza com contexto do projeto |
| init-engram | Para agents novos (ex.: auth-expert): usa template ou scaffold |

**Efeito:** Compatível com o fluxo atual; adiciona customização e variantes.

---

## 5. Recomendação: Abordagem A

Motivos:

1. Skills e agents passam a ter o mesmo fluxo: templates + genesis.
2. `.claude/` nasce vazio (exceto estrutura) e é preenchido só pelo init-engram.
3. Cada projeto recebe apenas os agents necessários.
4. Customização explícita no init-engram.

### 5.1 O que mudaria

| Componente | Mudança |
|------------|---------|
| **templates/agents/** | Criar pasta e mover conteudo de `core/agents/` para `.agent.tmpl` |
| **setup.sh** | Copiar `templates/agents/` para `.claude/templates/agents/` |
| **setup.sh** | Remover cópia de `core/agents/` para `.claude/agents/` |
| **generate_component.py** | Para agent: buscar template (ex.: `db-expert-prisma` quando orm=prisma) |
| **analyze_project.py** | Já sugere agents; pode refinar nomes (ex.: `db-expert-prisma` quando Prisma) |
| **init-engram** | Já chama genesis para agents; usar templates resolve a customização |

### 5.2 Regra de template matching (agents)

```
Sugestão: db-expert, orm=prisma
  → Buscar: db-expert-prisma.agent.tmpl
  → Se não achar: db-expert.agent.tmpl
  → Se não achar: scaffold genérico

Sugestão: architect
  → Buscar: architect.agent.tmpl
  → Se não achar: scaffold
```

### 5.3 Customização

O template fornece a base. O init-engram (Claude) ajusta:

- `project_name`, `framework`, `orm`, `pkg_manager`
- Referências diretas ao projeto (pastas, scripts)
- Skills referenciados em `skills:` no frontmatter

Placeholders como `${FRAMEWORK}`, `${ORM}`, ou seções específicas podem ser substituídos durante o init-engram.

---

## 6. Fluxo Final (Visão)

```
setup.sh
  → DNA, Genesis, Evolution, seeds, commands
  → templates/skills/ → .claude/templates/skills/
  → templates/agents/ → .claude/templates/agents/  [NOVO]
  → knowledge/ (estrutura)
  → .claude/agents/ vazio  [MUDANÇA]

init-engram
  → analyze_project: stack + sugestões (skills + agents)
  → Plano: Skills e Agents a gerar
  → Para cada aprovado:
      - Skill: generate_component → template ou scaffold → customizar
      - Agent: generate_component → template ou scaffold → customizar
  → Popular knowledge
  → Popular cérebro

Resultado: .claude/ com skills e agents específicos para o projeto
```

---

## 7. Resumo

| Antes | Depois |
|-------|--------|
| setup copia 3 agents finais | setup copia templates de agents para staging |
| init-engram não gera agents | init-engram gera agents a partir de templates |
| Agents idênticos em todos os projetos | Agents customizados por projeto |
| Skills com templates, agents sem | Skills e agents com o mesmo fluxo |

A adição de `templates/agents/` fecha essa lacuna e alinha agents ao fluxo de skills.
