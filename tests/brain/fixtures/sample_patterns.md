# Project Patterns

## Padrões Aprovados

### PAT-001: Feedback Loop
- **Contexto**: After any task
- **Solução**: Run /learn to register changes. References [[ADR-001]].
- **Descoberto em**: 2026-01-15

### PAT-002: Deterministic IDs
- **Contexto**: When creating nodes
- **Solução**: Use md5(title|labels)[:8] for dedup. See [[ADR-002]].
- **Descoberto em**: 2026-01-20

## Anti-Patterns

### ANTI-001: UUID for Node IDs
- **Contexto**: Old code used uuid4
- **Problema**: Caused duplicate nodes on repeated add_memory calls
- **Solução**: Replaced with deterministic md5 hash
