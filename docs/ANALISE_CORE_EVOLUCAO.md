# Análise: Core (DNA, Genesis, Evolution) — Evolução para que o Projeto Evolua

> Análise aprofundada do core metacircular para identificar pontos sólidos e oportunidades de melhoria.

---

## 1. DNA — Avaliação

### 1.1 Estado Atual

| Schema | Cobertura | Consistência | Observações |
|--------|-----------|--------------|-------------|
| **skill.schema.md** | ✅ Completo | ✅ | Frontmatter (name, description, composes, version), body, validação clara |
| **agent.schema.md** | ✅ Completo | ✅ | Regras de não-encadeamento, tools, skills |
| **command.schema.md** | ✅ Completo | ⚠️ | Exemplo no schema usa recall (brain) — OK para v4 |
| **knowledge.schema.md** | ✅ Completo | ✅ | CURRENT_STATE genesis-only documentado |

### 1.2 Conclusão DNA

**DNA está OK.** Os schemas são bem definidos, as regras são claras e o validate.py cobre a maior parte. Nenhuma mudança estrutural necessária.

### 1.3 Pequenas Melhorias (Opcional)

| # | Melhoria | Prioridade | Esforço |
|---|----------|------------|---------|
| D1 | Adicionar `version` como campo obrigatório no skill.schema (validate já aceita) | Baixa | Trivial |
| D2 | Validar que `composes:` aponta para skills existentes (validate.py com --project-dir) | Média | Baixo |
| D3 | Validar que agent `skills:` aponta para skills existentes | Média | Baixo |

---

## 2. Genesis — Avaliação

### 2.1 O Que Funciona Bem

| Componente | Avaliação |
|------------|-----------|
| **analyze_project.py** | Stack detection robusta (Node, Python, PHP, Rust, Go, Ruby; Next.js, Django, FastAPI, NestJS, Laravel, etc.) |
| **generate_component.py** | Templates em staging, scaffold genérico OK, kebab-case validation |
| **validate.py** | Cobre skill, agent, command, manifest; frontmatter parsing correto |
| **register.py** | Manifest atualizado, activations, versioning, --activate |
| **compose.py** | Resolve cadeias composes:, detecta ciclos, gera plano de ativação |
| **skill-patterns.md** | Referências boas (workflow linear, decisão+ação, template, análise+report) |

### 2.2 Gaps Identificados

| # | Gap | Impacto | Onde |
|---|-----|---------|------|
| **G1** | **analyze_project não sugere commands** | Projetos com fluxos específicos (deploy, migrate) não recebem sugestão de command | suggest_components() |
| **G2** | **Scaffold de command muito fraco** | generate_command gera 5 linhas genéricas; nenhum padrão útil | generate_component.py |
| **G3** | **Template matching usa .claude/templates** | setup.sh copia templates/ para .claude/; mas staging em init-engram usa outra pasta | Fluxo init-engram |
| **G4** | **curriculum.py duplica detecção de stack** | analyze_project.py tem stack completa; curriculum tem detect_stack_simple — divergência | curriculum.py vs analyze_project.py |
| **G5** | **Agents sugeridos são sempre os mesmos 3** | G1.1 do GAPS: não há agents por stack (auth-expert, k8s-expert, etc.) | analyze_project.py |
| **G6** | **Sem validação de composes no validate** | composes: [skill-x] pode apontar para skill inexistente | validate.py |
| **G7** | **generate_agent não usa contexto do projeto** | Scaffold genérico; não menciona Prisma, NextAuth, etc. | generate_component.py |

### 2.3 Recomendações Genesis

| Prioridade | Ação | Esforço | Impacto |
|------------|------|---------|---------|
| **Alta** | G5: Expandir suggest_components() com agents por stack (auth, infra, cache) | Médio | Alto |
| **Alta** | G2: Enriquecer scaffold de command — padrões como status, plan, deploy | Baixo | Alto |
| **Média** | G1: Sugerir commands baseado em stack (deploy se docker, migrate se ORM) | Baixo | Médio |
| **Média** | G6: validate.py --project-dir para validar composes e agent skills | Baixo | Médio |
| **Média** | G4: curriculum.py reusar analyze_project.detect_stack() em vez de duplicar | Baixo | Consistência |
| **Baixa** | G7: generate_agent aceitar --context com framework/orm do projeto | Médio | Médio |

---

## 3. Evolution — Avaliação (Foco Principal)

### 3.1 O Que Funciona

| Script | Função | Status |
|--------|--------|--------|
| **track_usage.py** | health, stale, summary | ✅ Funciona |
| **co_activation.py** | pares + grupos de skills juntos | ✅ Funciona (dados em evolution-activations.json) |
| **archive.py** | backup versionado, restore | ✅ Funciona |
| **curriculum.py** | cobertura de skills vs stack | ✅ Funciona |
| **doctor.py** | health check estrutura + components | ✅ Funciona |
| **global_memory.py** | export/import entre projetos | ⚠️ Lê .md, não brain (gap v4) |

### 3.2 Gaps Críticos — Evolution NÃO Evolui de Fato

| # | Gap | Impacto | Detalhe |
|---|-----|---------|---------|
| **E1** | **Activation tracking 100% manual** | Evolution não tem dados reais de uso | register.py --activate precisa ser chamado por CADA skill usado. Ninguém faz isso. |
| **E2** | **co_activation --log-session manual** | Co-ativação depende de Claude lembrar e listar skills | learn.md manda rodar `--log-session --skills a,b,c` — frágil |
| **E3** | **evolution-log.md nunca é escrito** | Decisões evolutivas não ficam rastreadas | SKILL diz "registrar em evolution-log.md"; nenhum script escreve |
| **E4** | **Detector de skill grande (split) não existe** | "SKILL.md > 400 linhas" é descrito no SKILL mas não implementado | track_usage não checa tamanho |
| **E5** | **Propostas evolutivas não são acionáveis** | Output é texto; não há JSON para automação | /learn poderia consumir evolution --report --json |
| **E6** | **Evolution não sugere agents** | G4.1 GAPS: evolution foca em skills; agentes evoluem só por orquestração | track_usage/curriculum não consideram agents |
| **E7** | **doctor não integra brain health** | cognitive.py health existe; doctor não chama | learn diz rodar cognitive; doctor poderia incluir |
| **E8** | **global_memory lê .md, não brain** | v4: brain é fonte; export de pattern/experience vem de .md obsoleto | global_memory.py |

### 3.3 Fluxo Atual vs Desejado

```
ATUAL (quebrado):
  Sessão → Claude usa skills A, B, C (implícito)
  /learn → Claude DEVE: 1) lembrar quais foram A,B,C
                         2) rodar register --activate para cada
                         3) rodar co_activation --log-session --skills A,B,C
  → Ninguém faz isso consistentemente. evolution-activations.json tem dados
    porque algumas sessões registraram; manifest activations está defasado.

DESEJADO:
  Opção A: Claude no /learn SEMPRE produz "Skills usados: [lista]" no final
           → Script evolution/session_summary.py --skills A,B,C
             que chama register --activate + co_activation --log-session
  Opção B: Inferir do diff da sessão (arquivos .claude/skills/X tocados)
           → Menos preciso
  Opção C: Padronizar: /learn Fase 5 exige output estruturado
           {"skills_used": [...], "agents_used": [...], "commands_used": [...]}
           → Pipe para script que atualiza tudo
```

### 3.4 Recomendações Evolution (Priorizadas)

| Prioridade | Ação | Esforço | Impacto |
|------------|------|---------|---------|
| **CRÍTICA** | E1+E2: Criar `session_summary.py` que recebe lista de skills/agents usados e chama register + co_activation | Baixo | Alto |
| **CRÍTICA** | Integrar session_summary no /learn: Fase 5 exige que Claude liste componentes usados → pipe para script | Baixo | Alto |
| **Alta** | E4: Adicionar em track_usage.py --report oversized (skills com SKILL.md > 400 linhas) | Trivial | Médio |
| **Alta** | E3: evolution propose.py ou similar que escreve em evolution-log.md quando proposta aprovada | Baixo | Médio |
| **Alta** | E5: track_usage.py --report evolution --json (propostas em formato máquina) | Médio | Médio |
| **Média** | E6: curriculum/evolution sugerir agents faltantes (ex: auth muito usado, auth-expert não existe) | Médio | Médio |
| **Média** | E7: doctor.py --with-brain chama cognitive.py health quando .claude/brain existe | Trivial | Baixo |
| **Baixa** | E8: global_memory exportar do brain quando disponível (ou doc clarificar que .md é fallback) | Alto | Baixo |

---

## 4. Resumo Executivo

### DNA
- **Status:** OK, sem mudanças urgentes
- **Ação:** Manter; melhorias D2/D3 (validação cross-ref) são opcionais

### Genesis
- **Status:** Bom, com gaps de sugestão e scaffold
- **Ações prioritárias:**
  1. Agents por stack (auth-expert, etc.)
  2. Command scaffold mais rico
  3. validate --project-dir para composes

### Evolution
- **Status:** Conceito certo, execução quebrada — dados de uso não fluem
- **Ações prioritárias:**
  1. **session_summary.py** — entrada única para "quais componentes foram usados"
  2. **Integrar no /learn** — Fase 5 output estruturado → script
  3. **track_usage --report oversized** — detectar skills para split
  4. **evolution-log auto-escrita** — quando proposta aprovada

### Princípio para Evolução Real

> **O projeto só evolui se os dados de uso fluírem.** Hoje:
> - manifest activations = manual (quase nunca atualizado)
> - evolution-activations.json = parcial (quando alguém lembra de logar)
> - evolution-log.md = vazio (ninguém escreve)
>
> **Fix:** Um único ponto de entrada no /learn: Claude declara o que usou → script propaga tudo.

---

## 5. Plano de Implementação Sugerido

### Fase 1 — Evolution Funcional (1–2 dias)
1. Criar `core/evolution/scripts/session_summary.py`:
   - `--skills a,b,c --agents x,y --commands z`
   - Chama register --activate para cada
   - Chama co_activation --log-session --skills a,b,c
2. Atualizar `core/commands/learn.md` Fase 5:
   - "Ao final, liste os componentes usados nesta sessão"
   - Instruir: rodar session_summary.py com a lista
3. Adicionar `track_usage.py --report oversized`

### Fase 2 — Genesis Melhorado (1 dia)
1. analyze_project: agents por stack (auth, infra)
2. generate_component: command scaffold com padrões (status, plan)
3. validate: --project-dir para composes

### Fase 3 — Polish (opcional)
1. evolution propose → escreve evolution-log
2. doctor --with-brain
3. curriculum reusar analyze_project.detect_stack
