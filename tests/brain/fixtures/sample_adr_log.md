# Architecture Decision Records

## ADR-001: Use FallbackGraph
**Data**: 2026-01-15
**Status**: Aceito

### Contexto
NetworkX is a heavy dependency. Not all environments have it installed.

### Decisão
Implement a FallbackGraph class that provides basic graph operations when NetworkX is not available.

### Consequências
- Works without external dependencies
- Limited functionality compared to NetworkX

---

## ADR-002: Deterministic Node IDs
**Data**: 2026-01-20
**Status**: Aceito
**Relacionado**: [[ADR-001]]

### Contexto
Using uuid4 for node IDs causes duplicates when the same memory is added twice.

### Decisão
Use md5(title|labels) truncated to 8 chars as deterministic ID. Same input always produces same ID.

### Consequências
- Automatic dedup via upsert
- Predictable IDs for testing
- Risk of collision (low with 8 hex chars)
