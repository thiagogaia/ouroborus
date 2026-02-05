# ADR-000: Inspiração Arquitetural (Voyager + DGM + BOSS)

**ID**: 79abc0a5
**Autor**: [[@engram]]
**Data**: 2026-02-05
**Labels**: Decision, ADR

---

## Contexto
Antes de criar o Engram v2, foi realizada pesquisa de soluções de mercado para sistemas auto-alimentados. Três projetos se destacaram como inspiração arquitetural:

1. **Voyager (NVIDIA/MineDojo)**: Agente de Minecraft que constrói sua própria biblioteca de skills à medida que explora. Skills simples compõem skills complexos.

2. **Darwin Gödel Machine (Sakana AI)**: Agente que reescreve seu próprio código-fonte. Mantém arquivo evolutivo de todas as versões.

3. **BOSS (Bootstrap Your Own Skills - USC/Google)**: Bootstrapping bottom-up de skills através de prática. Skills emergem de padrões detectados.

## Decisão
Combinar as melhores ideias de cada projeto:

| Projeto | Conceito Adotado | Implementação no Engram |
|---------|------------------|-------------------------|
| Voyager | Skill Library composicional | `composes:` em SKILL.md + co_activation.py |
| Voyager | Verificação antes de commit | validate.py obrigatório |
| DGM | Arquivo evolutivo | .claude/versions/ + archive.py |
| DGM | Sistema modifica a si mesmo | engram-genesis pode gerar si mesmo |
| BOSS | Skill emergente de padrão | /learn detecta padrões → propõe skill |
| BOSS | Composição bottom-up | co_activation.py → sugere composite |

## Consequências
- ✅ Fundação conceitual sólida baseada em pesquisa
- ✅ Cada feature tem justificativa acadêmica
- ✅ Roadmap claro derivado de gaps identificados
- ⚠️ Algumas features (curriculum automático) ainda não implementadas
- ⚠️ Experiential replay ainda não integrado

### Referências

- Voyager Paper: https://arxiv.org/abs/2305.16291
- DGM Paper: Sakana AI (2024)
- BOSS Paper: USC/Google (NeurIPS 2023)
- Documento completo: `Engram_self_bootstrap_analysis.md`

