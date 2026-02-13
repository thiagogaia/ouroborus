# Análise: Update vs Extras

> Decisão: extras no install sim, no update não. Análise do fluxo de update.

---

## 1. Contexto

- **Extras como padrão no install**: setup.sh passaria a incluir extras automaticamente na instalação inicial.
- **Update**: O usuário questionou se extras deveriam entrar no `--update`. Conclusão: analisar o fluxo antes de decidir.

---

## 2. Fluxo do Update (setup.sh --update)

O `do_update()` faz:

| Etapa | Ação | Preserva customizações? |
|-------|------|-------------------------|
| 1 | Pre-flight: Engram instalado? | — |
| 2 | Comparação de versão | — |
| 3 | **Backup** de todo .claude/ | — |
| 4 | DNA (schemas) | Sobrescreve |
| 5 | Genesis, Evolution | Sobrescreve |
| 6 | Seeds | Sobrescreve (com aviso de arquivos locais) |
| 7 | **Agents** | **Sobrescreve** `core/agents/*.md` → `.claude/agents/` |
| 8 | Commands | Sobrescreve |
| 9 | Skill templates | Sobrescreve |
| 10 | Brain scripts | Sobrescreve (código; dados preservados) |
| 11 | Manifest | Atualiza versão; adiciona novos seeds se não existirem |

---

## 3. Cenário de Uso do Update

Projeto que já passou por:

1. **setup.sh** (install) — instalou core + extras
2. **init-engram** — fez prune, create, customize:
   - Removeu agents desnecessários (ex.: db-expert em projeto sem DB)
   - Criou agents faltantes (ex.: auth-expert)
   - Customizou os que ficaram (ex.: db-expert-prisma)

3. **Tempo passa** — Engram ganha nova versão (correções, melhorias no Genesis, etc.)

4. **setup.sh --update** — usuário quer atualizar o core

---

## 4. O que o Update deve fazer

Objetivo: **atualizar o motor** (DNA, Genesis, Evolution, scripts) sem invalidar o trabalho já feito.

- **DNA, Genesis, Evolution**: refresh de schemas e scripts — faz sentido
- **Seeds**: refresh de skills universais — faz sentido (com cuidado para customizações)
- **Agents**: hoje o update **sobrescreve** core/agents em .claude/agents/

Risco: se o projeto tinha architect, db-expert customizados pelo init-engram, o update sobrescreve com as versões “virgens” do core. O backup mitiga, mas a escolha de design é clara: update trata core como “fonte de verdade” e substitui.

---

## 5. Extras no Update — por que não

Se o update passasse a incluir extras:

| Situação | Efeito |
|----------|--------|
| Projeto tinha init-engram e **removeu** infra-expert (sem infra) | Update reintroduziria infra-expert — conflita com o prune |
| Projeto tem infra-expert **customizado** | Update sobrescreveria com versão base |
| Projeto tem devops-patterns **customizado** | Sobrescreveria com versão base |
| Projeto nunca teve extras (instalado antes dessa mudança) | Adicionaria extras — pode ser desejado, mas não é o cenário principal |

O update é usado em projetos **já inicializados**. O conjunto de agents/skills já foi definido pelo init-engram (prune/create/customize). Reintroduzir ou sobrescrever extras nesse momento:

- Desfaz decisões do prune
- Desfaz customizações
- Muda o propósito do update (de “refresh do motor” para “expandir componentes”)

---

## 6. Conclusão (atualizada)

| Fluxo | Extras? | Justificativa |
|-------|---------|---------------|
| **Install** (setup.sh) | ✅ Sim | Instalação inicial deve ter palette completa para o init-engram decidir (prune/create/customize). |
| **Update** (setup.sh --update) | ✅ Sim | Após update, o usuário roda /init-engram que faz as comparações necessárias com os arquivos de backup (prune/create/customize). O install_extras adiciona novos extras e preserva existentes (skip). |

---

## 7. Projeto instalado antes de “extras no install”

Se o setup passou a incluir extras no install, projetos antigos (instalados antes) não terão extras.

Opções:

- **A**: Manter `install_extras.sh` para quem quiser adicionar extras manualmente em projetos existentes.
- **B**: Documentar que “extras no install” vale só para instalações novas; para projetos antigos, usar `install_extras.sh` se quiser.

Recomendação: **manter install_extras.sh** como comando para “adicionar extras a projeto existente”.
