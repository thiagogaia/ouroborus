# Análise de Implementação — Engram v3

> Baseado na análise da base CenterPag (Monetizze) — 39 markdowns, 28+ microserviços

---

## Bugs Encontrados

### Bug 1: Laravel nunca é detectado ✅ CORRIGIDO

O `detect_stack()` detectava PHP (`composer.json` existe) mas nunca setava `framework = "laravel"`.
O check `if fw == "laravel"` era dead code. O `setup.sh` tinha o mesmo bug.

**Fix**: Parser de `composer.json` para `laravel/framework` em `analyze_project.py` e `setup.sh`.
**Commit**: `9cbb313`

### Bug 2: Faltam detecções ✅ CORRIGIDO

- NestJS — adicionado via `@nestjs/core` em `analyze_project.py` e `setup.sh`
- Sequelize — adicionado em `setup.sh`
- Guards `[[ -z "$FRAMEWORK" ]]` — corrigidos no `setup.sh` para nuxt/angular/sveltekit

**Commit**: `9cbb313`

---

## Plano de Implementação — Status

### templates/stacks/ (receitas por framework)

| # | Item | Status | Commit |
|---|------|--------|--------|
| 1 | `nestjs/nestjs-patterns.skill.tmpl` | ✅ Done | `9cbb313` |
| 2 | `flask/flask-patterns.skill.tmpl` | ✅ Done | — |
| 3 | `laravel/` (já existia, fix no detection) | ✅ Done | `9cbb313` |

### core/ (melhorias universais)

| # | Item | Status | Commit |
|---|------|--------|--------|
| 4 | Fix `analyze_project.py` — NestJS/Laravel/Flask detection | ✅ Done | `9cbb313` |
| 5 | `base-ingester` seed skill + `/ingest` command | ✅ Done | `e9841a0` |

### templates/knowledge/ (knowledge files)

| # | Item | Status | Commit |
|---|------|--------|--------|
| 6 | `SERVICE_MAP.md.tmpl` | ✅ Done | — |

### extras/skills/ (skills de nicho)

| # | Item | Status | Notas |
|---|------|--------|-------|
| 7 | `microservices-navigator/` | ⏳ Esqueleto criado | Falta SKILL.md + references |
| 8 | `devops-patterns/` | ⏳ Esqueleto criado | Falta SKILL.md + references |
| 9 | `fintech-domain/` | ⏳ Esqueleto criado | Falta SKILL.md + references |
| 10 | `execution-pipeline/` | ⏳ Esqueleto criado | Falta SKILL.md + references |

### extras/agents/ (agents de nicho)

| # | Item | Status | Notas |
|---|------|--------|-------|
| 11 | `infra-expert.md` | ❌ Não iniciado | — |

---

## Descrição dos Itens Pendentes

### 7. microservices-navigator (extras/skills/)

Para ecossistemas de microserviços (como CenterPag). Cobre:
- Mapa de dependências entre serviços
- Detecção de comunicação (REST, Kafka, SQS, gRPC)
- Identificação de duplicidades
- Padrões de orquestração (conductor, saga, choreography)

### 8. devops-patterns (extras/skills/)

Padrões de infra e DevOps:
- GitOps (ArgoCD, Flux)
- Kubernetes (HPA, PDB, Rollouts, Ingress)
- CI/CD pipelines (GitLab, GitHub Actions)
- Secrets management (External Secrets, IRSA)
- Canary/Blue-Green deployments

### 9. fintech-domain (extras/skills/)

Para projetos de pagamento/fintech:
- Entidades: Client, Payment Operator, Business Operator, Seller
- Fluxos: Order → Charge → Transaction → Settlement
- Compliance: CERC, PCI, PLD, KYC
- Padrões: Split de pagamento, antifraude, chargeback

### 10. execution-pipeline (extras/skills/)

Inspirado no metodo-execucao.md da Monetizze:
- 7 estágios: Planejamento → Implementação → Teste → Avaliação → Doc → Release → Wiki
- Artefatos rastreáveis (cenarios-teste.md, resultado-teste.md)
- Loop de correção com retry limit
- Integra com /plan, /review, /commit

### 11. infra-expert agent (extras/agents/)

Agent especializado em infraestrutura:
- Kubernetes, Docker, CI/CD
- AWS/GCP/Azure patterns
- Monitoramento (Prometheus, Grafana)
- Debugging de deploy/scaling

---

## Prioridade Sugerida (restantes)

| Prioridade | Item | Esforço | Impacto |
|------------|------|---------|---------|
| 1 | microservices-navigator | Médio | Alto (nicho) |
| 2 | devops-patterns | Médio | Alto (nicho) |
| 3 | fintech-domain | Médio | Alto (nicho) |
| 4 | execution-pipeline | Alto | Médio |
| 5 | infra-expert agent | Baixo | Médio |
