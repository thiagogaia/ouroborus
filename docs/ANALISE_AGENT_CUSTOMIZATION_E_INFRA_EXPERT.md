# Análise: agent-customization-guide e infra-expert

> Pontos levantados: onde vai o agent-customization-guide no projeto destino? infra-expert em core vs extras?

---

## 1. agent-customization-guide.md — Onde vai no projeto destino?

### 1.1 Fluxo do setup.sh

O setup **não copia a pasta `core/`** para o projeto. Ele **distribui o conteúdo** de core em `.claude/`:

```bash
# setup.sh install_core (linhas 219-221)
cp -r "$SCRIPT_DIR/core/genesis" "$CLAUDE_DIR/skills/engram-genesis"
```

Ou seja:
- `core/genesis/` (inteiro) → `TARGET_DIR/.claude/skills/engram-genesis/`
- Inclui `core/genesis/references/` → `.claude/skills/engram-genesis/references/`
- Inclui `core/genesis/scripts/` → `.claude/skills/engram-genesis/scripts/`

### 1.2 Conclusão: o guide vai para o projeto

| Repositório Engram (source) | Projeto destino (após setup) |
|-----------------------------|------------------------------|
| `core/genesis/references/agent-customization-guide.md` | `.claude/skills/engram-genesis/references/agent-customization-guide.md` |

O guide **existe** no projeto destino. Ele fica dentro do skill engram-genesis.

### 1.3 Momento de uso: /init-engram

- `/init-engram` roda **no contexto do projeto** (projeto com `.claude/` já instalado).
- Nesse momento a pasta `core/` **não existe** no projeto — só o que foi copiado para `.claude/`.
- O caminho correto para o init-engram usar é:

```
.claude/skills/engram-genesis/references/agent-customization-guide.md
```

### 1.4 Referência no init-engram

O comando `init-engram` deve indicar esse caminho, por exemplo:

```
Leia .claude/skills/engram-genesis/references/agent-customization-guide.md 
antes de customizar cada agent.
```

### 1.5 Resumo

| Pergunta | Resposta |
|----------|----------|
| Onde o guide é criado no repo? | `core/genesis/references/agent-customization-guide.md` |
| Onde ele fica no projeto destino? | `.claude/skills/engram-genesis/references/agent-customization-guide.md` |
| O `core/` existe no projeto? | Não. Só `.claude/` e seu conteúdo. |
| O guide é usado só no /init-engram? | Sim. É referência para a fase de customização de agents. |

---

## 2. core/agents/infra-expert.md vs extras/agents/infra-expert.md

### 2.1 Situação atual

| Local | Existe? | Instalado por |
|-------|---------|---------------|
| `core/agents/infra-expert.md` | ❌ Não | — |
| `extras/agents/infra-expert.md` | ✅ Sim | `install_extras.sh` (opcional) |

O setup **não** instala extras. O `install_extras.sh` é separado e opcional.

### 2.2 Conteúdo do extras/agents/infra-expert.md

O agent em extras é um agent completo e funcional:

- Frontmatter: name, description, tools, skills (devops-patterns)
- Responsabilidades: troubleshooting, CI/CD, Kubernetes, secrets
- Antes de diagnosticar: recall, PATTERNS, devops-patterns
- Seções: Kubernetes, Pipeline CI/CD, Secrets, checklist por tipo de problema
- Regras e guardrails

Ajustes menores: alguns acentos (Voce → Você, padroes → padrões).

### 2.3 Seriam parecidos?

Sim. O plano propõe criar `core/agents/infra-expert.md`.

**Opção A — Usar extras como base**  
Copiar `extras/agents/infra-expert.md` para `core/agents/infra-expert.md` e:

- Corrigir acentuação
- Checar schema (agent.schema.md)
- Conferir skills referenciados (devops-patterns existe em extras, não no core)

**Opção B — Criar de novo**  
Escrever novo agent em core inspirado no extras, mantendo estrutura e responsabilidades.

### 2.4 Diferença de instalação

| Cenário | core/agents/infra-expert | extras/agents/infra-expert |
|---------|---------------------------|----------------------------|
| setup.sh | Copiado para `.claude/agents/` em todo projeto | Não instalado |
| install_extras.sh | — | Copiado para `.claude/agents/` se o usuário rodar |

**Impacto de colocar infra-expert no core:**

- Todo projeto passa a ter infra-expert após o setup.
- O fluxo prune no init-engram remove se o projeto não tiver infra (sem K8s, Terraform, etc.).

**Impacto de manter só em extras:**

- Só quem rodar `install_extras.sh` terá infra-expert.
- O init-engram pode precisar criar infra-expert quando detectar infra — e não haveria base no core.

### 2.5 Recomendação

1. **Criar `core/agents/infra-expert.md`** com base em `extras/agents/infra-expert.md`.
2. **Corrigir** acentuação e alinhar ao schema.
3. **Dependência do skill**: `devops-patterns` está em extras. Duas opções:
   - (a) Fazer o инфра-expert funcionar sem skill (skills vazio ou opcional).
   - (b) Mover `devops-patterns` para core (seeds ou templates) para que o infra-expert funcione mesmo sem extras.
4. **Extras**: manter `extras/agents/infra-expert.md` como variante opcional ou deprecated em favor do core.

### 2.6 Conteúdo esperado de core/agents/infra-expert.md

Estrutura equivalente ao extras:

- Mesmas responsabilidades
- Mesmos checklists (Kubernetes, CI/CD, Secrets)
- Mesmas regras e guardrails
- `skills: [devops-patterns]` se o skill existir no projeto; caso contrário, instruções básicas no body

---

## 3. Resumo das correções no plano

### 3.1 agent-customization-guide

- **Criar em**: `core/genesis/references/agent-customization-guide.md`
- **Referência no init-engram**: `.claude/skills/engram-genesis/references/agent-customization-guide.md`
- **Uso**: Somente during /init-engram, fase de customização de agents.

### 3.2 infra-expert

- **Criar** `core/agents/infra-expert.md` baseado em `extras/agents/infra-expert.md`.
- **Diferenças**: correção de acentuação, validação contra schema, tratamento do skill devops-patterns.
- **Extras**: decidir se `extras/agents/infra-expert.md` continua como variante ou é substituído pelo core.
