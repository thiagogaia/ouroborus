# PAT-012: Venv Isolado para Brain

**ID**: d0b05c77
**Autor**: [[@engram]]
**Data**: 2026-02-05
**Labels**: Pattern, ApprovedPattern

---

- **Contexto**: dependências Python pesadas (torch, sentence-transformers)
- **Solução**: criar venv em `.claude/brain/.venv`
  - setup.sh cria e instala deps automaticamente
  - Scripts do brain ativam venv antes de executar
  - Evita conflitos com Python do sistema
  - Permite embeddings locais sem cloud
- **Exemplo**: `source .claude/brain/.venv/bin/activate && python3 brain.py stats`
- **Descoberto em**: 2026-02-03
