# Avaliação do Plano de Implementação — Agents Prune, Spawn, Customize

> Checklist de assertividade antes de prosseguir com a implementação.

---

## ✅ Pontos corretos

| Item | Status |
|------|--------|
| prune_agents: interface, lógica, segurança | OK |
| analyze_project: customization, auth-expert, infra-expert | OK |
| Sem agent-bases, scaffold + Claude | OK |
| auth-expert somente em extras | OK |
| Backup unificado (.claude.bak) | OK |
| Separação init-engram vs update-engram | OK |
| Ordem de implementação | OK |
| agent-customization-guide em genesis/references | OK |
| generate_component já usa scaffold | OK (não busca agent-bases) |

---

## 🔴 Correções necessárias no plano

### 1. Linha 27 — Fluxo pós-update

**Atual**: "Após update: O usuário roda `/init-engram` para fazer as comparações necessárias..."

**Correto**: "Após update: O usuário roda `/update-engram` para migrar, prune/customize agents e apagar backups."

### 2. Fase 2.5 vs Fase 3 do init-engram

O plano diz inserir Fase 2.5 "entre Fase 2 e Fase 3". A Fase 3 atual trata "skills e agents" juntos. Com a Fase 2.5:

- **Fase 2.5**: Agents (prune → create → customize)
- **Fase 3**: Skills (a parte de agents sai da Fase 3)

O plano deve deixar explícito que a Fase 3 passa a tratar **apenas skills**. Os agents são responsabilidade da Fase 2.5.

### 3. Referências "Se houve migração" no init-engram

O init-engram **não faz mais migração**. Ainda há 3 ocorrências em Fase 4:

- PATTERNS.md: "Se houve migração: verificar se padrões do backup ainda são válidos"
- DOMAIN.md: "Se houve migração: mesclar termos do backup"
- EXPERIENCE_LIBRARY.md: "Se houve migração: manter experiências do backup"

**Correção**: Essas situações só ocorrem no `/update-engram`. No init-engram, remover ou substituir por "N/A — init cria do zero".

### 4. Tarefa 8 — update-engram já existe

O `core/commands/update-engram.md` já foi criado. A tarefa 8 deveria ser:

- **"Integrar Fase 2.5 Agents no update-engram"** (a Fase 4 está como placeholder)

### 5. Tarefa 4 — generate_component

O `generate_component.py` atual já gera scaffold genérico para agents, sem agent-bases. A tarefa 4 pode ser:

- **"Verificar generate_component"** — garantir que não há referência a agent-bases (já está correto).
- Ou **remover** a tarefa 4 se não houver mudanças.

### 6. prune_agents — Formato de --remove

O plano mostra `--remove db-expert auth-expert`. É preciso definir:

- `--remove db-expert auth-expert` (múltiplos como posicionais)
- ou `--remove db-expert --remove auth-expert` (append)
- ou `--remove "db-expert,auth-expert"` (string com separador)

Sugestão: `--remove` com `nargs='*'` ou lista separada por vírgula, como em `--needed`.

---

## ❓ Perguntas para o usuário

### 1. Fase 2.5 — Skills ou só agents?

A Fase 2.5 do plano trata **apenas agents**. As **skills** continuam na Fase 3 "Auto-Geração via Genesis"?

Ou a Fase 2.5 deve incluir também prune/customize de skills (por exemplo, remover skills não usadas)?

### 2. Ordem Fase 2.5 vs Fase 3

Ordem atual proposta: Fase 2 (Plano) → Fase 2.5 (Agents) → Fase 3 (Skills).

O plano de geração (Fase 2) deve listar **skills e agents** e o dev aprova os dois. Depois:

- Fase 2.5: executa agents (prune, create, customize)
- Fase 3: executa skills (generate, customize)

Confirma que essa ordem está correta?

### 3. Confirmação antes do prune

O plano diz "Init-engram pergunta confirmação antes de prune". O plano apresentado ao dev (Fase 2) já inclui "Agents: Remover: [to_remove]". O dev aprova o plano inteiro. Isso conta como confirmação ou deve haver uma confirmação específica só para o prune?

---

## 📋 Resumo das correções a aplicar no plano

1. Linha 27: trocar init-engram por update-engram no fluxo pós-update.
2. Partes 5 e 7: explicitar que Fase 3 = skills, Fase 2.5 = agents.
3. init-engram: remover ou ajustar referências a "Se houve migração" na Fase 4.
4. Tarefa 8: renomear para "Integrar Fase 2.5 no update-engram".
5. Tarefa 4: marcar como "Verificar" ou remover.
6. Parte 1: especificar formato exato de `--remove` (ex.: vírgula ou múltiplos args).

---

## Próximo passo

Após suas respostas e aprovação, o plano será corrigido e a implementação pode seguir.
