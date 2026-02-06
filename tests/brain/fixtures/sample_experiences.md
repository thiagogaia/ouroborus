# Experience Library

## EXP-001: Debug Brain Load Failure
- **Contexto**: Brain failed to load after corrupted JSON
- **Stack**: Python, brain.py
- **Abordagem**:
1. Check if graph.json exists
2. Validate JSON syntax
3. Rebuild from knowledge files if corrupt
- **Resultado**: Sucesso
- **Data**: 2026-01-15

---

## EXP-002: Optimize Sleep Cycle
- **Contexto**: Sleep cycle was too slow on large graphs. Related to [[PAT-001]].
- **Stack**: Python, sleep.py
- **Abordagem**:
1. Profile phase_relate — O(n^2) comparisons
2. Limit pairs to 500 nodes max
3. Use TF vectors instead of full embeddings
- **Resultado**: Sucesso — 10x faster
- **Data**: 2026-01-20
