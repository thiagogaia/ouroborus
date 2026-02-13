# Análise: templates/ vs extras/ — Similaridades e Fluxo Correto

> As duas pastas guardam componentes por contexto, mas o fluxo de instalação é diferente e incompleto.

---

## 1. Conteúdo Atual

### templates/

| Tipo | Estrutura | Formato | Uso |
|------|-----------|---------|-----|
| **knowledge** | 6 arquivos .md.tmpl | Estrutura + ${DATE} | setup.sh substitui e cria .claude/knowledge/ |
| **skills** | 11 pastas por framework | .skill.tmpl | setup → staging → genesis usa no init-engram |

```
templates/
├── knowledge/           # Estrutura base (setup, uma vez)
│   ├── context/CURRENT_STATE.md.tmpl
│   ├── priorities/PRIORITY_MATRIX.md.tmpl
│   ├── patterns/PATTERNS.md
│   └── ...
└── skills/              # Por framework (genesis, init-engram)
    ├── nextjs/nextjs-patterns.skill.tmpl
    ├── django/django-patterns.skill.tmpl
    ├── fastapi/fastapi-patterns.skill.tmpl
    └── ... (11 frameworks)
```

### extras/

| Tipo | Estrutura | Formato | Uso |
|------|-----------|---------|-----|
| **skills** | 4 pastas completas | SKILL.md + references/ | install_extras.sh (manual) |
| **agents** | 2 arquivos .md | Agent completo | install_extras.sh (manual) |

```
extras/
├── skills/
│   ├── devops-patterns/     # K8s, CI/CD, GitOps
│   ├── fintech-domain/      # Pagamentos, fintech
│   ├── n8n-agent-builder/   # N8N + WhatsApp
│   └── sales-funnel-optimizer/
└── agents/
    ├── infra-expert.md      # DevOps, usa devops-patterns
    └── prompt-engineer.md   # Prompt engineering
```

---

## 2. Similaridades

| Aspecto | templates/skills | extras/skills |
|---------|------------------|---------------|
| **Contexto** | framework (nextjs, django) | nicho (devops, fintech) |
| **Formato** | .tmpl (scaffolding) | SKILL.md completo |
| **Sugestão** | analyze_project por framework | analyze_project por infra (só devops-patterns) |
| **Objetivo** | Skill customizado por projeto | Skill pronto para nicho |

Ambos são “skills por contexto”: templates por stack, extras por domínio.

---

## 3. Fluxo Atual (e Problemas)

### templates/skills → init-engram

```
setup.sh
  → cp templates/skills/* → .claude/templates/skills/

init-engram Fase 1-2
  → analyze_project sugere "nextjs-patterns"
  → Plano: "Skills a gerar: nextjs-patterns"

init-engram Fase 3
  → generate_component --type skill --name nextjs-patterns
  → Busca .claude/templates/skills/**/nextjs-patterns.skill.tmpl
  → Usa template ✓
  → Claude customiza
```

Fluxo correto.

### extras/skills → init-engram (quebrado)

```
setup.sh
  → NÃO copia extras

init-engram Fase 1-2
  → analyze_project sugere "devops-patterns" (source: extras) quando K8s/Terraform detectado
  → Plano: "Skills a gerar: devops-patterns"

init-engram Fase 3
  → generate_component --type skill --name devops-patterns
  → Busca .claude/templates/skills/**/devops-patterns.skill.tmpl
  → NÃO ENCONTRA (extras não está em staging)
  → Gera scaffold genérico ❌
  → Sobrescreve ou ignora o devops-patterns real de extras
```

Ou seja: quando o plano inclui um extra sugerido, o genesis trata como skill normal e gera scaffold em vez de usar o conteúdo de extras.

### extras/agents → nunca sugeridos

- `analyze_project` sugere apenas: db-expert, architect, domain-analyst.
- `infra-expert` (extras) não é sugerido quando infra é detectada.
- `infra-expert` depende de `devops-patterns`.
- Fluxo atual: o usuário precisa rodar `install_extras.sh` manualmente.

---

## 4. Inconsistências

| # | Problema | Impacto |
|---|----------|---------|
| 1 | **devops-patterns** sugerido mas não instalado no init-engram | Sugestão não vira instalação |
| 2 | **infra-expert** não sugerido quando infra detectada | Par devops-patterns + infra-expert não é oferecido |
| 3 | **generate_component** não consulta extras | Sempre cai em scaffold quando não há .tmpl |
| 4 | **templates** = scaffolding; **extras** = completos | Conceito diferente; ambos “por contexto” |
| 5 | **install_extras** instala tudo de uma vez | Não há instalação só dos sugeridos (ex.: devops) |

---

## 5. Proposta de Fluxo Unificado

### 5.1 Regra por tipo

| Tipo | Onde | Quando usar |
|------|------|-------------|
| **Template** | templates/ | Scaffolding para customização (framework, stack) |
| **Extra** | extras/ | Componente completo para nicho/domínio |

### 5.2 Integração no init-engram

Para cada item sugerido por `analyze_project`:

| source | Ação |
|--------|------|
| **(nenhum)** | `generate_component` → template ou scaffold |
| **extras** | Copiar de `extras/skills/{name}/` ou `extras/agents/{name}.md` |

Ou seja: quando `source == "extras"`, o init-engram deve instalar a partir de `extras/`, não chamar `generate_component`.

### 5.3 Ajustes em analyze_project

- Incluir `infra-expert` quando infras (K8s, Terraform, etc.) forem detectadas.
- Manter `source: "extras"` para skills/agents que vêm de extras.

### 5.4 Novos passos no init-engram (Fase 3)

```
Para cada componente aprovado:
  Se source == "extras":
    Copiar de extras/skills/{name}/ ou extras/agents/{name}.md
    Registrar no manifest com source: "extras"
  Senão:
    generate_component → template ou scaffold
    Validar, registrar
```

### 5.5 Papel do setup.sh

- **Templates:** continuar copiando para staging (como hoje).
- **Extras:** não copiar tudo no setup; instalar sob demanda no init-engram quando o item for sugerido e aprovado.

`install_extras.sh` continua útil para quem quer instalar todos os extras de uma vez, sem passar pelo init-engram.

---

## 6. Estrutura Unificada (Conceitual)

```
templates/
├── knowledge/     # Estrutura, setup uma vez
├── skills/        # Por framework — scaffolding (.tmpl)
└── agents/        # (novo) Por stack — scaffolding (.agent.tmpl)

extras/
├── skills/        # Por nicho — completos (SKILL.md)
└── agents/        # Por nicho — completos (.md)

Fluxo:
  analyze_project sugere { name, source: "template" | "extras" }
  init-engram:
    - source template → generate_component (usa .tmpl ou scaffold)
    - source extras   → copiar de extras/
```

---

## 7. Resumo de Mudanças Sugeridas

| # | Mudança | Onde |
|---|---------|------|
| 1 | **init-engram Fase 3** | Se `source == "extras"`, copiar de extras/ em vez de generate_component |
| 2 | **analyze_project** | Sugerir `infra-expert` (agent) quando infra detectada |
| 3 | **generate_component** | (Opcional) Se não achar template, checar extras/ antes de scaffold |
| 4 | **extras como staging** | (Opcional) setup copiar extras para `.claude/extras-staging/` para init-engram usar |

---

## 8. Conclusão

`templates` e `extras` são similares no sentido de “componentes por contexto”, mas o fluxo trata só `templates` corretamente. `extras` são sugeridos e nunca instalados no init-engram.

Fluxo desejado:

- **templates** → scaffolding, customização via genesis.
- **extras** → componentes completos instalados quando sugeridos e aprovados no init-engram.
