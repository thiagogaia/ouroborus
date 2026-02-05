# ADR-013: Remoção de Componentes Órfãos (Ciclo Ouroboros)

**ID**: 53e1ed87
**Autor**: [[@engram]]
**Data**: 2026-02-05
**Labels**: Decision, ADR

---

## Contexto
Análise da ANALISE_IMPLEMENTA.md revelou que 3 componentes não participavam do ciclo ouroboros:
- `execution-pipeline`: duplicava /plan→/review→/commit→/learn, assumia Docker obrigatório
- `microservices-navigator`: fora do escopo local (análise cross-repo), overlap de 40% com base-ingester
- `SERVICE_MAP.md.tmpl`: nenhum skill, command ou workflow o lia ou atualizava

## Decisão
Remover os 3 componentes. O Engram é local e metaprogramável — usuários criam skills sob demanda com `/create` se precisarem de pipeline rígido ou navegação de microserviços.

## Consequências
- ✅ Menos peso morto em extras/ (362 linhas removidas)
- ✅ Princípio claro: componente sem consumidor = remover
- ✅ Reforça filosofia de geração sob demanda vs pré-fabricação
- ⚠️ Usuários que esperavam esses extras precisam criar via /create

