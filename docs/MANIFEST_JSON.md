# Como o manifest.json funciona

Documento de referência sobre o registro central de componentes do Engram.

## 1. Estrutura do arquivo

```
.claude/manifest.json
├── engram_version      → versão do Engram (ex: "4.0.0")
├── installed_at        → data/hora da instalação inicial
├── last_updated        → última alteração
├── components
│   ├── skills          → {"nome": { metadados }}
│   ├── agents          → {"nome": { metadados }}
│   └── commands        → {"nome": { metadados }}
├── evolution
│   ├── total_generations   → componentes novos registrados
│   ├── total_evolutions    → componentes atualizados
│   └── total_archived      → componentes arquivados
└── notes               → texto livre (opcional)
```

### Metadados por componente

| Campo | Tipo | Significado |
|-------|------|-------------|
| `version` | string | Ex: "1.0.0" |
| `source` | string | `core`, `seed`, `genesis`, `runtime`, `extras`, `manual`, `evolution` |
| `created_at` | ISO datetime | Quando foi registrado |
| `updated_at` | ISO datetime | Última atualização de metadados |
| `activations` | int | Número de vezes que foi usado |
| `last_used` | ISO datetime ou null | Última vez que foi usado |
| `health` | string | `active` ou `archived` |
| `description` | string | Só em commands |

---

## 2. Ciclo de vida

### 2.1 Criação (setup.sh install)

Quando roda `./setup.sh`:

1. Se `manifest.json` não existe, cria com:
   - `engram_version` do `VERSION`
   - `installed_at` e `last_updated`
   - `components.skills` com skills de core/seed (engram-genesis, engram-evolution, project-analyzer, etc.)
   - `components.agents` e `components.commands` vazios
   - `evolution` zerado

2. Não sobrescreve manifest existente (projeto já configurado).

### 2.2 Atualização (setup.sh --update)

Em `./setup.sh --update`:

1. `update_manifest_json()` é chamado
2. Atualiza:
   - `engram_version` e `last_updated`
   - Novos seeds em `core/seeds/` que ainda não estão no manifest (nunca sobrescreve existentes)
3. Usa Python inline para ler/escrever JSON

### 2.3 Registro de componente (register.py)

```bash
python3 register.py --type skill --name my-skill --source genesis --project-dir .
```

**Se novo:** adiciona em `components.skills` (ou agents/commands) com `version`, `source`, `created_at`, `updated_at`, `activations=0`, `last_used=null`, `health=active`. Incrementa `evolution.total_generations`.

**Se existente:** atualiza `version`, `updated_at`, `source`. Incrementa `evolution.total_evolutions`.

### 2.4 Desregistro (register.py --unregister)

```bash
python3 register.py --unregister --type skill --name my-skill --project-dir .
```

- Marca `health=archived`
- Incrementa `evolution.total_archived`
- Não remove dados nem arquivos em disco

### 2.5 Registro de ativação (register.py --activate)

```bash
python3 register.py --activate --type skill --name knowledge-manager --project-dir .
```

- Chamado quando um skill/agent/command é usado em sessão
- Incrementa `activations`
- Define `last_used` = agora

### 2.6 Extras (install_extras.sh)

Ao instalar extras:

- Lê `manifest.json`
- Adiciona skills de `extras/skills/` e agents de `extras/agents/` com `source=extras`
- Atualiza `last_updated`

---

## 3. Quem usa o manifest

| Consumidor | Operação | O que usa |
|------------|----------|-----------|
| **setup.sh** | write | Criação e update de versão/seeds |
| **register.py** | read/write | Registro, unregister, activate, list |
| **install_extras.sh** | read/write | Registro de extras |
| **doctor.py** | read | Sync manifest↔disco, runtime components |
| **track_usage.py** | read | health, stale, summary |
| **curriculum.py** | read | Skills instalados, gaps de uso |
| **archive.py** | read | Versão para backups versionados |
| **generate_component.py** | read | Verificar se similar já existe |
| **validate.py** | read | Validar estrutura do manifest |

---

## 4. Evolução vs Co-ativação

Existem **dois fluxos** de métricas:

| Arquivo | Função |
|---------|--------|
| **manifest.json** | Por componente: activations, last_used, health, source |
| **evolution-activations.json** | Por sessão: quais skills foram usados juntos |

**evolution-activations.json** (exemplo):

```json
[
  {"timestamp": "2026-02-07T23:26:22", "skills": ["domain-expert", "engram-genesis", "knowledge-manager"]},
  ...
]
```

- Usado por `co_activation.py` para detectar pares de skills usados juntos
- Complementa o manifest (sessões vs. uso por componente)

---

## 5. Significado de `source`

| Source | Quando |
|--------|--------|
| `core` | engram-genesis, engram-evolution, agents (architect, db-expert, domain-analyst) |
| `seed` | project-analyzer, knowledge-manager, domain-expert, etc. |
| `genesis` | Skill gerado por generate_component.py |
| `runtime` | Componente criado durante sessão |
| `extras` | Instalado via install_extras.sh |
| `manual` | Registrado manualmente |
| `evolution` | Resultado de evolução/composição |

---

## 6. Fluxo resumido

```
┌─────────────────────────────────────────────────────────────────┐
│                     CRIAÇÃO / ATUALIZAÇÃO                        │
├─────────────────────────────────────────────────────────────────┤
│  setup.sh install    → Cria manifest com skills core/seed        │
│  setup.sh --update   → Atualiza version + novos seeds           │
│  install_extras.sh   → Adiciona extras                          │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                     REGISTRO DE COMPONENTES                     │
├─────────────────────────────────────────────────────────────────┤
│  generate_component → cria skill/agent em disco                  │
│  register.py        → adiciona ao manifest (source=genesis)      │
│  /create, /spawn     → chamam register.py após gerar             │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                     DURANTE O USO                               │
├─────────────────────────────────────────────────────────────────┤
│  Claude usa skill X  → /learn chama register.py --activate       │
│  co_activation       → loga sessão em evolution-activations.json │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                     RELATÓRIOS / DIAGNÓSTICO                     │
├─────────────────────────────────────────────────────────────────┤
│  track_usage        → health, stale, summary (lê manifest)      │
│  doctor             → sync manifest↔disco, runtime components   │
│  curriculum         → gaps de uso                                │
└─────────────────────────────────────────────────────────────────┘
```

---

## 7. Pontos sensíveis

1. **Orphans** — manifest referencia componente que não existe mais no disco
2. **Não registrados** — componente existe no disco mas não no manifest
3. **Sem histórico** — só `activations` e `last_used`; não há log por ativação
4. **Concorrência** — dois writes simultâneos podem corromper o JSON
5. **--activate manual** — precisa ser chamado em `/learn`; se esquecer, métricas ficam desatualizadas

---

## Referências

- ADR-006: Manifest como Source of Truth
- register.py: `.claude/skills/engram-genesis/scripts/register.py`
- track_usage.py: `.claude/skills/engram-evolution/scripts/track_usage.py`
