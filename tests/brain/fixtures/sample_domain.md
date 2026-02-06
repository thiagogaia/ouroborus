# Domain Knowledge

## Glossário

**Engram**: Memory trace stored in the brain. Persistent memory system for Claude Code.

**FallbackGraph**: Simplified graph when NetworkX is unavailable. Provides add_node, add_edge, successors, predecessors.

**Decay Rate**: Rate at which memory strength diminishes over time. Lower values mean slower forgetting.

## Regras de Negócio

- **RN-001**: Memories with strength below 0.1 should be archived.
- **RN-002**: Person and Domain nodes are never archived (protected labels).

## Entidades

**Brain**: Core knowledge graph that stores all memories, connections, and embeddings.

**Memory**: A node in the knowledge graph with title, content, labels, and memory state.
