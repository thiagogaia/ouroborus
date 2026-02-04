# commit-5da6535c: Definicao da Arquitetura v3.0

**ID**: 8293d12d
**Autor**: [[{'email': 'thiagogaia@gmail.com', 'name': 'Thiago Gaia', 'username': '@thiagogaia'}]]
**Data**: 2026-02-04
**Labels**: Episode, Architecture, Documentation, Milestone

---

Commit que define a arquitetura completa do Engram v3.0:
- ADR-008: Arquitetura Git-Native com Grafo de Conhecimento estilo Obsidian
- ADR-009: Estado por Desenvolvedor (state/dev.md evita conflitos)
- ADR-010: Convencao de Commits de Conhecimento (knowledge(@autor): ...)
- ADR-011: Cerebro Organizacional com NetworkX + embeddings

Decisoes de escalabilidade:
- 10 devs x 5 anos = ~25k episodios = ~50MB (Git aguenta)
- Custo: ~/bin/zsh.20/sessao (vs  sem otimizacao)
- Camadas HOT/WARM/COLD para tokens

Modelo Obsidian:
- [[wikilinks]] para criar grafo emergente
- Backlinks gerados automaticamente
- INDEX.md eliminado (grafo eh o indice)
