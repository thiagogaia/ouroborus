# ADR-012: Separação setup.sh e batch-setup.sh

**ID**: f045840e
**Autor**: [[@engram]]
**Data**: 2026-02-05
**Labels**: Decision, ADR

---

## Contexto
O setup.sh acumulou funcionalidade de batch (múltiplos diretórios, `--batch` flag, progress indicator, summary) que aumentou o arquivo em +175 linhas (783 → 958) e misturou lógica de loop com lógica de instalação.

## Decisão
Reverter setup.sh para versão single-project e criar batch-setup.sh como wrapper que chama setup.sh em loop.

## Consequências
- ✅ setup.sh voltou a ser simples e focado (783 linhas)
- ✅ batch-setup.sh é independente e descartável (177 linhas)
- ✅ Unix philosophy restaurada
- ⚠️ Dois arquivos para manter ao invés de um

