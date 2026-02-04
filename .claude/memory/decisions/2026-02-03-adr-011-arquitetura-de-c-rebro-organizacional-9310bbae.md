# ADR-011: Arquitetura de Cérebro Organizacional

**ID**: 9310bbae
**Autor**: [[@engram]]
**Data**: 2026-02-03
**Labels**: Decision, ADR

---

## Contexto
O Engram precisa de um sistema de memória que funcione como um cérebro organizacional real:
- Memória episódica (experiências), semântica (conceitos), procedural (patterns)
- Consolidação (fortalecer memórias importantes)
- Esquecimento (decay de memórias não acessadas)
- Busca semântica (por significado, não só texto)
- Grafo de conhecimento (relações tipadas entre conceitos)

Escala alvo: dezenas de desenvolvedores trabalhando por anos.

## Decisão
Implementar arquitetura híbrida:

## Consequências
**Benefícios:**
- ✅ Grafo real com travessia O(1) em memória
- ✅ Git-friendly (JSON é texto, embeddings usa LFS)
- ✅ Busca semântica por significado
- ✅ Memórias decaem naturalmente (menos ruído)
- ✅ Spreading activation encontra conhecimento relacionado
- ✅ Escala para ~1M nós confortavelmente
- ✅ Dependência leve (só NetworkX e numpy)

**Trade-offs:**
- ⚠️ Precisa carregar grafo em memória (~200MB para 50k nós)
- ⚠️ Embeddings requerem regeneração se mudar modelo
- ⚠️ Merge de graph.json pode conflitar (resolver com rebuild)
- ⚠️ LFS necessário para embeddings.npz em repos grandes

**Métricas de Sucesso:**
- Tempo de carregamento < 2s
- Busca com spreading activation < 100ms
- Memórias relevantes no top 10 > 80% das vezes
- Decay remove >50% de ruído após 90 dias

