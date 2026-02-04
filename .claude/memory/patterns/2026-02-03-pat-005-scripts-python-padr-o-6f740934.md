# PAT-005: Scripts Python Padrão

**ID**: 6f740934
**Autor**: [[@engram]]
**Data**: 2026-02-03
**Labels**: Pattern, ApprovedPattern

---

- **Contexto**: ao criar scripts para skills
- **Solução**:
  - Shebang `#!/usr/bin/env python3`
  - Docstring com usage
  - argparse para CLI
  - Funções isoladas e testáveis
  - main() no final com if __name__ == "__main__"
- **Exemplo**: `core/genesis/scripts/validate.py`
- **Descoberto em**: 2026-02-03
