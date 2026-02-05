Inicializar o Engram para este projeto usando o sistema de auto-geração.

## Fase 0: Migração de Backup (se existir)

O setup.sh cria backups quando já existe configuração anterior.
Esta fase detecta, analisa e migra conteúdo customizado.

1. Execute a detecção de backups:
```bash
python3 .claude/skills/engram-genesis/scripts/migrate_backup.py --project-dir . --detect --output json
```

2. Se backups forem encontrados (`found: true`), execute análise completa:
```bash
python3 .claude/skills/engram-genesis/scripts/migrate_backup.py --project-dir . --analyze --output json
```

3. Apresente ao dev o que foi encontrado:
```
🔄 Backup Detectado — Análise de Migração
═════════════════════════════════════════

Componentes customizados encontrados:
  📦 Skills: [listar se houver]
  📦 Commands: [listar se houver]
  📦 Agents: [listar se houver]

Knowledge com conteúdo útil:
  📚 [arquivo]: [X linhas de conteúdo]

Permissões customizadas:
  ⚙️  [X] permissões adicionais detectadas

Recomendações:
  🔴 [alta prioridade]
  🟡 [média prioridade]

Estratégia: SMART (mesclar inteligentemente)
Continuar com migração? (perguntar ao dev)
```

4. Se aprovado, execute a migração:
```bash
python3 .claude/skills/engram-genesis/scripts/migrate_backup.py --project-dir . --migrate --strategy smart
```

5. **NÃO apague os backups ainda** — isso será feito na Fase Final.

Se não houver backups, pule para Fase 1.

## Fase 1: Análise do Projeto

1. Execute o analisador de projeto:
```bash
python3 .claude/skills/engram-genesis/scripts/analyze_project.py --project-dir . --output json
```

2. Leia o resultado e entenda a stack detectada e sugestões de componentes.

## Fase 2: Planejar Componentes

Cruzar três fontes de informação para montar o plano:

1. **Stack detectada** (resultado da Fase 1): framework, ORM, database, linguagem
2. **Template skills disponíveis** (em `.claude/templates/skills/`): listar as pastas — cada pasta é um template de skill nomeado pelo framework que atende
3. **Sugestões do analyze_project.py**: skills, agents e commands sugeridos

Para cada template em `.claude/templates/skills/`:
- Se o **nome da pasta** corresponde ao framework ou tecnologia detectada → marcar como INSTALAR
- Se não corresponde → marcar como DESCARTAR
- Se corresponde parcialmente (ex: `react/` num projeto Next.js) → avaliar e decidir

Para as sugestões do genesis:
- Se já existe um template que cobre a sugestão → usar o template (não gerar do zero)
- Se não existe template → marcar para gerar via genesis

Montar a lista unificada de componentes a criar.

## Fase 3: Apresentar Plano

Apresente ao dev o plano completo ANTES de executar:

```
🐍 Engram Init — Plano de Geração
═══════════════════════════════════

Stack detectada: [listar]

Skills a instalar:
  📦 [nome] — de template (match com stack detectada)
  🔧 [nome] — gerar via genesis (sem template disponível)

Skills descartados (sem match):
  ❌ [nome-patterns] — [framework] não detectado

Agents a gerar:
  🔧 [nome] — [razão]

Seeds universais (já instalados):
  ✅ [listar os seeds presentes em .claude/skills/]

[Se houve migração na Fase 0:]
Migrados do backup:
  ✅ [componentes preservados]

Continuar? (perguntar ao dev)
```

## Fase 4: Gerar e Instalar Componentes

Executar o plano aprovado. Para cada componente:

### Se veio de template:
1. Copiar `.skill.tmpl` para `.claude/skills/[nome]/SKILL.md`
2. **Customizar** o conteúdo para o projeto:
   - Trocar exemplos genéricos por exemplos reais encontrados no codebase
   - Ajustar nomes de entidades, rotas, serviços para os do projeto
   - Adicionar padrões específicos detectados na análise
3. Registrar via `register.py` com `--source template`

### Se gerado via genesis:
1. Gerar scaffold via `generate_component.py`
2. Customizar para o projeto (skills, agents, commands)
3. Validar via `validate.py`
4. Registrar via `register.py`

### Ao final:
Deletar staging area inteira:
```bash
rm -rf .claude/templates/
```

**Regra**: Template é ponto de partida, NÃO produto final. SEMPRE customizar para o projeto.

## Fase 5: Popular Knowledge

Preencher knowledge files com dados reais:

### CURRENT_STATE.md
- Analisar o codebase em profundidade
- Mapear módulos, dependências, estado de cada área
- Identificar dívidas técnicas
- Listar bloqueios conhecidos

### PATTERNS.md
- Inspecionar código existente
- Detectar padrões recorrentes (naming, estrutura, error handling)
- Registrar como padrões aprovados
- **Se houve migração**: verificar se padrões do backup ainda são válidos

### DOMAIN.md
- Analisar nomes de entidades, variáveis, tabelas
- Extrair glossário do domínio
- Mapear regras de negócio implícitas no código
- **Se houve migração**: mesclar termos do backup

### PRIORITY_MATRIX.md
- Buscar TODOs no código
- Identificar issues/bugs óbvios
- Priorizar com ICE Score

### EXPERIENCE_LIBRARY.md
- **Se houve migração**: manter experiências do backup
- Caso contrário: criar vazia (será populada pelo /learn)

## Fase 6: Popular Cérebro Organizacional

O cérebro em `.claude/brain/` deve ser populado com conhecimento existente.

### 6.1 Verificar venv do Brain
```bash
# Verifica se venv existe e ativa
if [[ -d ".claude/brain/.venv" ]]; then
    source .claude/brain/.venv/bin/activate
fi
```

### 6.2 Popular com conhecimento existente

Processar ADRs, conceitos de domínio, patterns e commits:
```bash
python3 .claude/brain/populate.py all
```

Isso irá:
- Extrair ADRs do ADR_LOG.md
- Extrair conceitos do DOMAIN.md (glossário, regras, entidades)
- Extrair patterns do PATTERNS.md
- Processar últimos 7000 commits do git (memória episódica)

### 6.3 Gerar Embeddings para Busca Semântica
```bash
python3 .claude/brain/embeddings.py build
```

### 6.4 Verificar Saúde do Cérebro
```bash
python3 .claude/brain/cognitive.py health
```

Se `status: healthy`, continuar. Se não, seguir recomendações.

### 6.5 Reportar ao Dev
```
🧠 Cérebro Organizacional Populado
══════════════════════════════════

Memórias criadas:
  📋 [X] ADRs (decisões arquiteturais)
  📚 [Y] Conceitos (glossário + regras)
  🔄 [Z] Patterns (padrões aprovados)
  📝 [W] Commits (memória episódica)

Total: [N] nós, [M] arestas
Grau médio: [G] (conectividade)
Embeddings: [E] vetores gerados

Status: 🟢 Saudável
```

---

## Fase 7: Health Check

Executar `/doctor` para validar a instalação completa.

## Fase 8: Cleanup e Relatório Final

1. **Se houve backup na Fase 0**, execute cleanup:
```bash
python3 .claude/skills/engram-genesis/scripts/migrate_backup.py --project-dir . --cleanup
```

3. Apresentar resumo do que foi:
   - Template skills instalados (da staging area)
   - Template skills removidos (sem match com stack)
   - Gerado via genesis (componentes adicionais)
   - Migrado (do backup, se houve)
   - Populado (knowledge files)
   - Validado (health check)

4. Sugerir próximos passos concretos baseado nas prioridades detectadas.

```
🐍 Engram Init — Concluído!
═══════════════════════════════════

✅ Template skills: X instalados, Y removidos
✅ Componentes gerados: X skills, Y agents
✅ Migrados do backup: Z items
✅ Knowledge populado: 7 arquivos
✅ Cérebro populado: N nós, M arestas, E embeddings
✅ Health check: PASSED

🗑️  Staging de templates removido
🗑️  Backups removidos (migração concluída)

Próximos passos sugeridos:
  1. [baseado em PRIORITY_MATRIX]
  2. [baseado em PRIORITY_MATRIX]
  3. [baseado em PRIORITY_MATRIX]

Use /status para ver o estado atual.
Use /learn após cada sessão para retroalimentar.
Use /recall para consultar o cérebro organizacional.
```
