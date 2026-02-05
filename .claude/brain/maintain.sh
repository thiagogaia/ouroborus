#!/bin/bash
# maintain.sh - Script de manutencao do cerebro organizacional
#
# Uso:
#   ./maintain.sh daily     # Roda decay (diario)
#   ./maintain.sh weekly    # Roda consolidate (semanal)
#   ./maintain.sh monthly   # Roda archive (mensal)
#   ./maintain.sh health    # Verifica saude
#   ./maintain.sh full      # Roda tudo + commit

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_DIR"

case "${1:-health}" in
    daily|decay)
        echo "=== Running Daily Decay ==="
        python3 .claude/brain/cognitive.py decay
        ;;

    weekly|consolidate)
        echo "=== Running Weekly Consolidation ==="
        python3 .claude/brain/cognitive.py consolidate
        ;;

    monthly|archive)
        echo "=== Running Monthly Archive ==="
        python3 .claude/brain/cognitive.py archive
        ;;

    sleep)
        echo "=== Running Sleep Cycle ==="
        python3 .claude/brain/sleep.py ${@:2}
        ;;

    health)
        echo "=== Brain Health Check ==="
        python3 .claude/brain/cognitive.py health
        ;;

    full)
        echo "=== Full Maintenance ==="
        python3 .claude/brain/cognitive.py decay
        python3 .claude/brain/sleep.py
        python3 .claude/brain/cognitive.py consolidate
        python3 .claude/brain/cognitive.py health

        echo ""
        echo "=== Committing changes ==="
        if git diff --quiet .claude/brain/graph.json 2>/dev/null; then
            echo "No changes to commit"
        else
            git add .claude/brain/graph.json
            git commit -m "chore(brain): maintenance run" --no-verify || true
            echo "Changes committed"
        fi
        ;;

    *)
        echo "Usage: $0 {daily|weekly|monthly|sleep|health|full}"
        echo ""
        echo "Commands:"
        echo "  daily    - Run memory decay (Ebbinghaus curve)"
        echo "  weekly   - Run connection consolidation"
        echo "  monthly  - Archive weak memories"
        echo "  sleep    - Run sleep cycle (semantic consolidation)"
        echo "  health   - Check brain health status"
        echo "  full     - Run all processes + commit"
        exit 1
        ;;
esac
