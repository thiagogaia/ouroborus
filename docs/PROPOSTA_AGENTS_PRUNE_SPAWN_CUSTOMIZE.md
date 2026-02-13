# Proposta: Agents — Prune, Spawn, Customize (sem templates)

> Análise da abordagem: verificar agents existentes, remover os desnecessários, criar os que faltam, customizar os que ficam.

---

## 1. Ideia

Agents são **específicos do projeto**. Em vez de templates:

1. **Analisar** o projeto e os agents existentes
2. **Remover** agents que o projeto não precisa
3. **Criar** (spawn) agents que faltam
4. **Customizar** os que permanecem

---

## 2. Fluxo Proposto

```
setup
  → Copia core/agents/ (3 universais: architect, db-expert, domain-analyst)
  → .claude/agents/ tem 3 arquivos

init-engram
  → analyze_project: stack + agents necessários
  → Lista agents existentes (diretório .claude/agents/)
  → Compara: necessários vs existentes

  Para cada agent existente:
    Se NÃO está em "necessários" → REMOVER (apagar arquivo + unregister)
    Se está em "necessários"    → CUSTOMIZAR (ajustar ao projeto)

  Para cada agent necessário que não existe:
    → SPAWN/CRIAR (generate_component + customizar)
```

---

## 3. Regras de Necessidade (em analyze_project hoje)

| Agent | Quando necessário | Implementado hoje? |
|-------|-------------------|--------------------|
| **architect** | Sempre | ✅ Sim |
| **domain-analyst** | Sempre | ✅ Sim |
| **db-expert** | Quando orm ou database detectado | ✅ Sim |
| **auth-expert** | Quando auth detectado (NextAuth, Clerk, etc.) | ❌ Não (só skill auth-patterns) |
| **infra-expert** | Quando infra detectada (K8s, Terraform, etc.) | ❌ Não (só skill devops-patterns) |

O `suggest_components` em `analyze_project.py` já condiciona db-expert:

```python
if stack.get("orm") or stack.get("database"):
    suggestions["agents"].append({"name": "db-expert", ...})
```

Projeto sem DB/ORM → analyze_project não sugere db-expert → init-engram pode remover.

---

## 4. Exemplos

### Projeto Next.js + Prisma
- Necessários: architect, domain-analyst, db-expert
- setup já instalou os 3
- Nenhum para remover
- Customizar db-expert (Prisma) e architect (Next.js)
- Não precisa criar nenhum

### Projeto React puro (sem backend)
- Necessários: architect, domain-analyst
- db-expert não é necessário
- Remover: db-expert
- Customizar: architect, domain-analyst
- Não precisa criar nenhum

### Projeto Next.js + Prisma + NextAuth
- Necessários: architect, domain-analyst, db-expert, auth-expert
- setup instalou 3; falta auth-expert
- Nenhum para remover
- Customizar: os 3 existentes
- Criar: auth-expert (spawn)

### Projeto com K8s + Terraform
- Necessários: architect, domain-analyst, infra-expert (e db-expert se tiver DB)
- setup instalou 3; falta infra-expert
- Criar: infra-expert (spawn ou copy de extras)

---

## 5. Ferramentas Existentes

| Ação | Ferramenta | Observação |
|------|------------|------------|
| **Remover** | register.py --unregister | Apenas marca archived no manifest; não apaga arquivo |
| **Criar** | generate_component.py | Gera scaffold; spawn usa isso |
| **Customizar** | Manual (Claude edita) | Não há script de customização |

Para remover de fato, falta:
- Apagar o arquivo (ex.: `.claude/agents/db-expert.md`)
- Chamar `register.py --unregister`

---

## 6. O Que Precisa Ser Feito

### 6.1 analyze_project

- Já retorna `suggestions.agents` com `name` e `reason`
- Possível evolução: incluir `agents_to_remove` (ex.: quando não há DB, sugerir remover db-expert)

### 6.2 Lógica de comparação

```
agents_needed = suggestions["agents"]  # lista de {name, reason}
agents_existing = listar .claude/agents/*.md

to_remove = agents_existing - agents_needed
to_keep = agents_existing ∩ agents_needed
to_create = agents_needed - agents_existing
```

### 6.3 Fluxo no init-engram

**Fase 3 (ou uma subfase de agents):**

1. Para cada agent em `to_remove`:
   - Apagar `.claude/agents/{name}.md`
   - `register.py --unregister --type agent --name {name}`

2. Para cada agent em `to_create`:
   - `generate_component.py --type agent --name {name}` (ou lógica de spawn)
   - Customizar para o projeto
   - Validar e registrar

3. Para cada agent em `to_keep`:
   - Customizar para o projeto (Claude edita o `.md` existente)

### 6.4 Script de remoção

Hoje não existe um script que delete o arquivo e faça unregister. Possível abordagem:

- **Opção A:** Novo script `prune_agents.py` que recebe lista e remove
- **Opção B:** Estender `register.py` com `--remove` que apaga o arquivo e desregistra
- **Opção C:** init-engram descreve os passos (apagar arquivo + unregister) e Claude executa

---

## 7. Customização de Agents Existentes

Para agents que ficam (to_keep), a customização pode incluir:

- Ajustar `description` ao stack (ex.: “Prisma”, “Next.js”)
- Atualizar `skills:` no frontmatter (ex.: adicionar prisma-workflow)
- Incluir instruções específicas (ex.: comandos Prisma, pastas do projeto)
- Manter guardrails e estrutura geral

Hoje isso é manual: Claude lê o agent, entende o projeto e edita o arquivo.

---

## 8. Spawn vs Create

| Comando | Uso | Fluxo |
|---------|-----|-------|
| **/create** | Interativo, detalhado | Pergunta propósito, gera, customiza, valida |
| **/spawn** | Rápido, durante tarefa | Gera com propósito da tarefa, source=runtime |

No init-engram, o fluxo é mais próximo de `/create`: propósito vem de `analyze_project`. O mecanismo é o mesmo: `generate_component` + customização. O “spawn” aqui é essa geração automática no init-engram, não o comando `/spawn` em si.

---

## 9. Comparação com Templates

| Abordagem | Prós | Contras |
|-----------|------|---------|
| **Templates** | Base pronta, pouco trabalho | Agents muito variados, poucos templates reutilizáveis |
| **Prune + Spawn + Customize** | Agents sempre alinhados ao projeto | Mais lógica no init-engram |

A abordagem prune/spawn/customize encaixa melhor quando agents são de fato específicos do projeto e não há um catálogo fixo de templates.

---

## 10. Resumo

| Elemento | Estado |
|----------|--------|
| **Remover agents** | Falta fluxo (apagar arquivo + unregister) |
| **Criar agents** | Já existe (generate_component) |
| **Customizar existentes** | Manual; pode ser guiado no init-engram |
| **Sugestões** | analyze_project já sugere agents necessários |
| **Lógica de comparação** | A implementar (needed vs existing) |

A ideia é viável e usa primitivas já existentes; o principal acrescentar é a lógica de prune e o suporte à remoção física de agents.

---

## 11. Plano de Implementação

Ver **`docs/PLANO_IMPLEMENTACAO_AGENTS_PRUNE_SPAWN_CUSTOMIZE.md`** para:
- prune_agents.py (interface, lógica, segurança)
- Aprimoramento do analyze_project (customization context, variantes)
- Casos inteligentes (db-expert-prisma, architect-nextjs, auth-expert, infra-expert)
- Integração no init-engram (Fase 2.5 Agents)
- Ordem de implementação e testes
