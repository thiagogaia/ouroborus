---                                                                                    
  Anatomia do Engram — Como cada camada funciona
                                                                                         
  core/ — O DNA (sempre instalado em todo projeto)
  O que: schemas/
  Para que: Contratos formais (skill, agent, command, knowledge)
  Como chega ao projeto: cp -r direto
  ────────────────────────────────────────
  O que: genesis/
  Para que: Motor que analisa projeto e gera componentes
  Como chega ao projeto: Vira skills/engram-genesis/
  ────────────────────────────────────────
  O que: evolution/
  Para que: Motor que rastreia uso e propõe melhorias
  Como chega ao projeto: Vira skills/engram-evolution/
  ────────────────────────────────────────
  O que: seeds/ (6)
  Para que: Skills universais (project-analyzer, code-reviewer, etc.)
  Como chega ao projeto: cp -r para skills/
  ────────────────────────────────────────
  O que: agents/ (3)
  Para que: Especialistas universais (architect, db-expert, domain-analyst)
  Como chega ao projeto: cp para agents/
  ────────────────────────────────────────
  O que: commands/ (15)
  Para que: Slash commands
  Como chega ao projeto: cp para commands/
  Regra: Se é útil em qualquer projeto, vai no core.

  templates/ — Scaffolding (usado durante install, nunca copiado inteiro)

  Duas sub-categorias:

  templates/knowledge/ — Templates de .md com ${DATE} substituído pelo setup.sh. Geram os
   arquivos iniciais em .claude/knowledge/. Usados uma vez na instalação, nunca mais.

  templates/stacks/ — Templates de skills por framework. O analyze_project.py detecta o
  framework → o genesis copia o .skill.tmpl correspondente como SKILL.md dentro de um
  novo skill. Funcionam como receitas pré-prontas que o genesis customiza.

  Regra: Se é um padrão que se repete entre projetos da mesma stack, vai em templates.

  extras/ — Opcionais (nunca instalados automaticamente)

  Skills e agents para nichos específicos. Hoje tem:
  - n8n-agent-builder — para quem automatiza vendas via N8N/WhatsApp
  - sales-funnel-optimizer — para quem otimiza funis de venda
  - prompt-engineer (agent) — para engenharia de prompts

  Regra: Se é útil só para um nicho/domínio específico, vai em extras. O dev instala via
  /import ou copia manual.

  ---
  Bugs encontrados na análise

  Bug 1: Laravel nunca é detectado pelo analyze_project.py

  O detect_stack() detecta PHP (composer.json existe) mas nunca seta framework =
  "laravel". O check na linha 233 (if fw == "laravel") é dead code — nunca é True.

  # Linha 44: detecta PHP mas não Laravel
  if (p / "composer.json").exists():
      stack["languages"].append("php")

  # Linha 233: NUNCA TRUE porque nenhum código seta framework="laravel"
  if stack.get("languages") and "php" in stack["languages"]:
      if fw == "laravel":  # ← fw nunca é "laravel"!

  O setup.sh tem o mesmo bug — detecta LANG_PHP=true mas nunca seta FRAMEWORK="laravel".

  Bug 2: Faltam detecções no detect_stack()

  - NestJS — nem detectado (CenterPag tem 10 serviços NestJS)
  - Flask — detectado mas sem template
  - Sequelize — detectado mas sem template/sugestão específica
  - MongoDB — detectado via mongoose mas não via composer.json (PHP)

  ---
  Sugestões revisadas (core / templates / extras)

  Para templates/stacks/ (novas receitas)

  1. templates/stacks/nestjs/nestjs-patterns.skill.tmpl

  NestJS é o framework mais popular de Node backend. CenterPag tem 10 serviços nele. O
  template deve cobrir:
  - Modules, Controllers, Services, Providers
  - DTOs com class-validator / class-transformer
  - Guards, Interceptors, Pipes
  - TypeORM/Sequelize/Mongoose integration patterns
  - Kafka consumers, SQS workers
  - Health checks (@nestjs/terminus)
  - Swagger decorators

  2. templates/stacks/flask/flask-patterns.skill.tmpl

  Flask é legado mas ainda amplamente usado. Template cobrindo:
  - Blueprints, Factory pattern (create_app)
  - Marshmallow schemas
  - SQLAlchemy session management
  - Error handlers

  3. templates/stacks/laravel/ (já existe, mas fix no detection)

  O template existe e é bom. O que falta é o detect_stack() e o setup.sh detectarem
  Laravel corretamente (ler composer.json e checar por laravel/framework).

  Para core/ (melhorias universais)

  4. Fix no analyze_project.py — detecção PHP/Laravel/NestJS

  Adicionar no detect_stack():
  # PHP frameworks via composer.json
  if "php" in stack["languages"]:
      composer_path = p / "composer.json"
      if composer_path.exists():
          composer = json.loads(composer_path.read_text())
          require = {**composer.get("require", {}), **composer.get("require-dev", {})}
          if "laravel/framework" in require:
              stack["framework"] = "laravel"

  # NestJS detection
  if "node" in stack["languages"] and "@nestjs/core" in deps:
      stack["framework"] = "nestjs"

  5. Skill: base-ingester (seed universal)

  O Engram hoje só absorve conhecimento incrementalmente via /learn. Não tem mecanismo
  para ingerir uma base de documentação inteira de uma vez (como a base CenterPag com 40+
   markdowns).

  Proposta como novo seed em core/seeds/base-ingester/:
  - Lê diretório de .md
  - Parseia tabelas, hierarquias, endpoints
  - Cria nós tipados no brain (Service, Entity, Rule, Endpoint)
  - Gera arestas automáticas (DEPENDS_ON, BELONGS_TO)
  - Gera embeddings incrementais
  - Command: /ingest [path] --type [domain|infra|services]

  Isso é universal — qualquer projeto pode ter docs externas para ingerir.

  6. Template: templates/knowledge/SERVICE_MAP.md.tmpl

  Novo knowledge file para projetos com múltiplos serviços/módulos:
  # Mapa de Serviços
  ## Serviços
  | Serviço | Stack | Responsabilidade | Dependências |
  ## Comunicação
  | De | Para | Protocolo | Tópico/Rota |
  ## Bancos de Dados
  | Serviço | Tipo | Schema |

  Para extras/ (skills de nicho)

  7. extras/skills/microservices-navigator/

  Para projetos que são ecossistemas de microserviços (como CenterPag). Não é universal o
   suficiente para seed, mas muito útil para quem trabalha com:
  - Mapa de dependências entre serviços
  - Detecção de comunicação (REST, Kafka, SQS, gRPC)
  - Identificação de duplicidades
  - Padrões de orquestração (conductor, saga, choreography)

  8. extras/skills/devops-patterns/

  Padrões de infra e DevOps:
  - GitOps (ArgoCD, Flux)
  - Kubernetes (HPA, PDB, Rollouts, Ingress)
  - CI/CD pipelines (GitLab, GitHub Actions)
  - Secrets management (External Secrets, IRSA)
  - Canary/Blue-Green deployments

  9. extras/skills/fintech-domain/

  Para projetos de pagamento/fintech:
  - Entidades: Client, Payment Operator, Business Operator, Seller
  - Fluxos: Order → Charge → Transaction → Settlement
  - Compliance: CERC, PCI, PLD, KYC
  - Padrões: Split de pagamento, antifraude, chargeback

  10. extras/skills/execution-pipeline/

  Inspirado no metodo-execucao.md da Monetizze. Para equipes que querem pipeline
  estruturado de tarefas:
  - 7 estágios: Planejamento → Implementação → Teste → Avaliação → Doc → Release → Wiki
  - Artefatos rastreáveis (cenarios-teste.md, resultado-teste.md)
  - Loop de correção com retry limit
  - Integra com /plan, /review, /commit

  11. extras/agents/infra-expert.md

  Agent especializado em infraestrutura:
  - Kubernetes, Docker, CI/CD
  - AWS/GCP/Azure patterns
  - Monitoramento (Prometheus, Grafana)
  - Debugging de deploy/scaling

  ---
  Prioridade de implementação
  ┌─────┬─────────────────────────────┬────────────┬─────────┬──────────────┐
  │  #  │            Item             │   Camada   │ Esforço │   Impacto    │
  ├─────┼─────────────────────────────┼────────────┼─────────┼──────────────┤
  │ 1   │ Fix detecção Laravel/NestJS │ core (bug) │ Baixo   │ Alto         │
  ├─────┼─────────────────────────────┼────────────┼─────────┼──────────────┤
  │ 2   │ Template NestJS             │ templates  │ Médio   │ Alto         │
  ├─────┼─────────────────────────────┼────────────┼─────────┼──────────────┤
  │ 3   │ base-ingester seed          │ core       │ Alto    │ Muito Alto   │
  ├─────┼─────────────────────────────┼────────────┼─────────┼──────────────┤
  │ 4   │ Template SERVICE_MAP        │ templates  │ Baixo   │ Médio        │
  ├─────┼─────────────────────────────┼────────────┼─────────┼──────────────┤
  │ 5   │ microservices-navigator     │ extras     │ Médio   │ Alto (nicho) │
  ├─────┼─────────────────────────────┼────────────┼─────────┼──────────────┤
  │ 6   │ devops-patterns             │ extras     │ Médio   │ Alto (nicho) │
  ├─────┼─────────────────────────────┼────────────┼─────────┼──────────────┤
  │ 7   │ fintech-domain              │ extras     │ Médio   │ Alto (nicho) │
  ├─────┼─────────────────────────────┼────────────┼─────────┼──────────────┤
  │ 8   │ execution-pipeline          │ extras     │ Alto    │ Médio        │
  ├─────┼─────────────────────────────┼────────────┼─────────┼──────────────┤
  │ 9   │ Flask template              │ templates  │ Baixo   │ Baixo        │
  └─────┴─────────────────────────────┴────────────┴─────────┴──────────────┘
