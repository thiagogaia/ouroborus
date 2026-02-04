# PAT-006: Registro em Manifest

**ID**: 02a48240
**Autor**: [[@engram]]
**Data**: 2026-02-03
**Labels**: Pattern, ApprovedPattern

---

- **Contexto**: ao criar/modificar componentes
- **Solução**: usar register.py para manter manifest.json sincronizado
  - `python3 register.py --type skill --name nome --source genesis`
  - Sources válidos: core, seed, genesis, manual, evolution, runtime
- **Descoberto em**: 2026-02-03
