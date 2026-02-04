#!/usr/bin/env python3
"""
cognitive.py - Processos cognitivos do cerebro

Jobs periodicos que mantem o cerebro saudavel:
- consolidate: Fortalece conexoes, detecta patterns
- decay: Aplica esquecimento (Ebbinghaus)
- archive: Move memorias fracas para arquivo

Uso:
    python cognitive.py consolidate    # Roda consolidacao
    python cognitive.py decay          # Roda decay
    python cognitive.py daily          # Roda decay (para cron diario)
    python cognitive.py weekly         # Roda consolidate (para cron semanal)
    python cognitive.py health         # Mostra saude do cerebro
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Importa o cerebro
sys.path.insert(0, str(Path(__file__).parent))
from brain import Brain


def consolidate(brain: Brain) -> dict:
    """
    Processo de consolidacao.

    Roda semanalmente para:
    - Fortalecer arestas entre nos co-acessados
    - Detectar patterns emergentes
    - Identificar hubs de conhecimento
    """
    stats = brain.consolidate()

    # Adiciona metadata
    stats["ran_at"] = datetime.now().isoformat()
    stats["type"] = "consolidate"

    return stats


def decay(brain: Brain) -> dict:
    """
    Processo de esquecimento.

    Roda diariamente para:
    - Aplicar curva de Ebbinghaus (decay exponencial)
    - Marcar memorias fracas
    - Identificar candidatos a arquivo
    """
    stats = brain.apply_decay()

    # Adiciona metadata
    stats["ran_at"] = datetime.now().isoformat()
    stats["type"] = "decay"

    return stats


def archive(brain: Brain, threshold: float = 0.1) -> dict:
    """
    Move memorias muito fracas para arquivo.

    Memorias com strength < threshold sao movidas para:
    .claude/archive/{year}/{node_id}.json
    """
    archive_path = brain.base_path.parent / "archive"
    year = str(datetime.now().year)
    year_path = archive_path / year
    year_path.mkdir(parents=True, exist_ok=True)

    archived = []
    nodes_to_remove = []

    # Identifica nos para arquivar
    for node_id in list(brain.graph.nodes):
        node = brain.get_node(node_id)
        if node is None:
            continue

        memory = node.get("memory", {})
        strength = memory.get("strength", 1.0)
        labels = node.get("labels", [])

        # Nao arquiva pessoas, dominios, decisions
        protected_labels = ["Person", "Domain", "Decision"]
        if any(l in labels for l in protected_labels):
            continue

        if strength < threshold:
            # Salva no arquivo
            archive_file = year_path / f"{node_id}.json"
            archive_file.write_text(
                json.dumps(node, indent=2, default=str),
                encoding='utf-8'
            )

            archived.append(node_id)
            nodes_to_remove.append(node_id)

    # Remove do grafo (em lote para evitar modificar durante iteracao)
    # Nota: NetworkX requer cuidado ao remover nos
    # Por ora, apenas marcamos como archived
    for node_id in nodes_to_remove:
        if node_id in brain.graph.nodes:
            brain.graph.nodes[node_id]["labels"] = (
                brain.graph.nodes[node_id].get("labels", []) + ["Archived"]
            )

    return {
        "archived_count": len(archived),
        "archived_nodes": archived[:20],
        "ran_at": datetime.now().isoformat(),
        "type": "archive"
    }


def health_check(brain: Brain) -> dict:
    """
    Verifica saude do cerebro.
    """
    stats = brain.get_stats()

    # Calcula metricas de saude
    total_nodes = stats.get("nodes", 0)
    weak_count = stats.get("weak_memories", 0)

    if total_nodes > 0:
        health_score = 1.0 - (weak_count / total_nodes)
    else:
        health_score = 1.0

    # Classifica saude
    if health_score >= 0.8:
        status = "healthy"
    elif health_score >= 0.5:
        status = "needs_attention"
    else:
        status = "critical"

    return {
        **stats,
        "health_score": round(health_score, 2),
        "status": status,
        "recommendations": get_recommendations(stats, health_score)
    }


def get_recommendations(stats: dict, health_score: float) -> list:
    """Gera recomendacoes baseadas no estado do cerebro."""
    recommendations = []

    weak_count = stats.get("weak_memories", 0)
    total_nodes = stats.get("nodes", 0)
    embeddings_count = stats.get("embeddings", 0)

    if weak_count > total_nodes * 0.3:
        recommendations.append({
            "type": "archive",
            "message": f"{weak_count} memorias fracas. Considere rodar 'cognitive.py archive'."
        })

    if embeddings_count < total_nodes * 0.5:
        recommendations.append({
            "type": "embeddings",
            "message": f"Apenas {embeddings_count}/{total_nodes} nos tem embeddings. Rode 'embeddings.py build'."
        })

    if total_nodes > 0 and stats.get("avg_degree", 0) < 2:
        recommendations.append({
            "type": "connections",
            "message": "Grafo pouco conectado. Adicione mais [[links]] nas memorias."
        })

    if not recommendations:
        recommendations.append({
            "type": "ok",
            "message": "Cerebro saudavel. Nenhuma acao necessaria."
        })

    return recommendations


def log_job(stats: dict, log_path: Path = None):
    """Loga resultado do job."""
    if log_path is None:
        log_path = Path(".claude/brain/cognitive-log.jsonl")

    log_path.parent.mkdir(parents=True, exist_ok=True)

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(stats, default=str) + "\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: cognitive.py <command>")
        print("Commands:")
        print("  consolidate    Run consolidation (weekly)")
        print("  decay          Run memory decay (daily)")
        print("  archive        Archive weak memories")
        print("  daily          Alias for decay")
        print("  weekly         Alias for consolidate")
        print("  health         Show brain health")
        sys.exit(1)

    cmd = sys.argv[1]

    brain = Brain()
    brain.load()

    if cmd in ["consolidate", "weekly"]:
        print("Running consolidation...")
        stats = consolidate(brain)
        brain.save()
        log_job(stats)
        print(json.dumps(stats, indent=2))

    elif cmd in ["decay", "daily"]:
        print("Running memory decay...")
        stats = decay(brain)
        brain.save()
        log_job(stats)
        print(json.dumps(stats, indent=2))

    elif cmd == "archive":
        print("Archiving weak memories...")
        stats = archive(brain)
        brain.save()
        log_job(stats)
        print(json.dumps(stats, indent=2))

    elif cmd == "health":
        print("Checking brain health...")
        stats = health_check(brain)
        print(json.dumps(stats, indent=2))

    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
