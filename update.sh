#!/usr/bin/env bash
set -euo pipefail

# ═══════════════════════════════════════════════════════════════
# Engram — Update (Three-Layer Ownership Model)
#
# Atualiza projetos com consciencia de 3 camadas:
#   Layer 1 (CORE-OWNED)    → sobrescreve sempre
#   Layer 2 (PROJECT-OWNED) → nunca toca
#   Layer 3 (RUNTIME)       → nunca toca
#
# Uso:
#   ./update.sh [TARGET_DIR]          # Update com drift report
#   ./update.sh --check [TARGET_DIR]  # Apenas reportar drift
#   ./update.sh --force [TARGET_DIR]  # Sem confirmacao
#   ./update.sh --regenerate [TARGET_DIR]  # Regenerar CLAUDE.md
# ═══════════════════════════════════════════════════════════════

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VERSION=$(cat "$SCRIPT_DIR/VERSION" 2>/dev/null || echo "unknown")

# ── Colors ────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

print_step() { echo -e "${BLUE}[$(date +%H:%M:%S)]${NC} ${GREEN}▸${NC} $1"; }
print_warn() { echo -e "${BLUE}[$(date +%H:%M:%S)]${NC} ${YELLOW}⚠${NC} $1"; }
print_done() { echo -e "${BLUE}[$(date +%H:%M:%S)]${NC} ${GREEN}✓${NC} $1"; }
print_err()  { echo -e "${BLUE}[$(date +%H:%M:%S)]${NC} ${RED}✗${NC} $1"; }

show_help() {
    echo ""
    echo -e "${BOLD}Engram v${VERSION} — Update${NC}"
    echo ""
    echo "Usage: ./update.sh [OPTIONS] [TARGET_DIR]"
    echo ""
    echo "Options:"
    echo "  --check        Only report drift (no changes)"
    echo "  --force        Skip confirmation prompts"
    echo "  --regenerate   Also regenerate CLAUDE.md and settings.json"
    echo "  -h, --help     Show this help"
    echo ""
    echo "Layers:"
    echo "  Layer 1 (CORE-OWNED)    commands, dna, genesis, evolution, seeds"
    echo "  Layer 2 (PROJECT-OWNED) agents, generated skills, knowledge, CLAUDE.md"
    echo "  Layer 3 (RUNTIME)       brain data, manifest, activations"
    echo ""
    exit 0
}

# ── Args ──────────────────────────────────────────────────────
MODE="update"    # update | check
FORCE=false
REGENERATE=false
TARGET_DIR=""

for arg in "$@"; do
    case "$arg" in
        --check)      MODE="check" ;;
        --force)      FORCE=true ;;
        --regenerate) REGENERATE=true ;;
        -h|--help)    show_help ;;
        *)            TARGET_DIR="$arg" ;;
    esac
done

TARGET_DIR="${TARGET_DIR:-.}"
TARGET_DIR="$(cd "$TARGET_DIR" 2>/dev/null && pwd)" || { print_err "Diretorio nao encontrado: $TARGET_DIR"; exit 1; }
CLAUDE_DIR="$TARGET_DIR/.claude"

# ── Pre-flight ────────────────────────────────────────────────

preflight() {
    if [[ ! -d "$CLAUDE_DIR" ]]; then
        print_err "Engram nao instalado em $TARGET_DIR"
        echo -e "  Use ${BOLD}./setup.sh $TARGET_DIR${NC} para instalar primeiro."
        exit 1
    fi

    local INSTALLED_VERSION
    INSTALLED_VERSION=$(cat "$CLAUDE_DIR/.engram-version" 2>/dev/null || echo "unknown")

    echo ""
    echo -e "${BOLD}Engram Update${NC}"
    echo -e "  Source:    ${CYAN}$SCRIPT_DIR${NC} (v${VERSION})"
    echo -e "  Target:    ${CYAN}$TARGET_DIR${NC} (v${INSTALLED_VERSION})"
    echo ""
}

# ═══════════════════════════════════════════════════════════════
# DRIFT DETECTION
# ═══════════════════════════════════════════════════════════════

declare -a DRIFT_LABELS=()
declare -a DRIFT_SOURCES=()
declare -a DRIFT_TARGETS=()
DRIFT_COUNT=0

check_pair() {
    local label="$1"
    local src="$2"
    local tgt="$3"

    if [[ -f "$src" && -f "$tgt" ]]; then
        if ! diff -q "$src" "$tgt" &>/dev/null; then
            DRIFT_LABELS+=("$label")
            DRIFT_SOURCES+=("$src")
            DRIFT_TARGETS+=("$tgt")
            DRIFT_COUNT=$((DRIFT_COUNT + 1))
        fi
    elif [[ -f "$src" && ! -f "$tgt" ]]; then
        DRIFT_LABELS+=("$label [NEW]")
        DRIFT_SOURCES+=("$src")
        DRIFT_TARGETS+=("$tgt")
        DRIFT_COUNT=$((DRIFT_COUNT + 1))
    fi
}

detect_drift() {
    print_step "Detectando drift em arquivos Layer 1..."

    # Commands
    for f in "$SCRIPT_DIR/core/commands/"*.md; do
        [[ -f "$f" ]] || continue
        local name
        name=$(basename "$f")
        check_pair "commands/$name" "$f" "$CLAUDE_DIR/commands/$name"
    done

    # DNA
    for f in "$SCRIPT_DIR/core/dna/"*.md; do
        [[ -f "$f" ]] || continue
        local name
        name=$(basename "$f")
        check_pair "dna/$name" "$f" "$CLAUDE_DIR/dna/$name"
    done

    # Genesis
    if [[ -d "$SCRIPT_DIR/core/genesis" ]]; then
        [[ -f "$SCRIPT_DIR/core/genesis/SKILL.md" ]] && \
            check_pair "genesis/SKILL.md" "$SCRIPT_DIR/core/genesis/SKILL.md" "$CLAUDE_DIR/skills/engram-genesis/SKILL.md"
        for f in "$SCRIPT_DIR/core/genesis/scripts/"*.py; do
            [[ -f "$f" ]] || continue
            local name
            name=$(basename "$f")
            check_pair "genesis/scripts/$name" "$f" "$CLAUDE_DIR/skills/engram-genesis/scripts/$name"
        done
        for f in "$SCRIPT_DIR/core/genesis/references/"*; do
            [[ -f "$f" ]] || continue
            local name
            name=$(basename "$f")
            check_pair "genesis/references/$name" "$f" "$CLAUDE_DIR/skills/engram-genesis/references/$name"
        done
    fi

    # Evolution
    if [[ -d "$SCRIPT_DIR/core/evolution" ]]; then
        [[ -f "$SCRIPT_DIR/core/evolution/SKILL.md" ]] && \
            check_pair "evolution/SKILL.md" "$SCRIPT_DIR/core/evolution/SKILL.md" "$CLAUDE_DIR/skills/engram-evolution/SKILL.md"
        for f in "$SCRIPT_DIR/core/evolution/scripts/"*.py; do
            [[ -f "$f" ]] || continue
            local name
            name=$(basename "$f")
            check_pair "evolution/scripts/$name" "$f" "$CLAUDE_DIR/skills/engram-evolution/scripts/$name"
        done
    fi

    # Seeds (only check SKILL.md of seeds that exist in both)
    for seed_dir in "$SCRIPT_DIR/core/seeds"/*/; do
        [[ -d "$seed_dir" ]] || continue
        local seed_name
        seed_name=$(basename "$seed_dir")
        if [[ -d "$CLAUDE_DIR/skills/$seed_name" ]]; then
            [[ -f "$seed_dir/SKILL.md" ]] && \
                check_pair "seeds/$seed_name/SKILL.md" "$seed_dir/SKILL.md" "$CLAUDE_DIR/skills/$seed_name/SKILL.md"
        fi
    done

    # Brain scripts (code only — .py, .sh, .md)
    if [[ -d "$SCRIPT_DIR/.claude/brain" && -d "$CLAUDE_DIR/brain" ]]; then
        # Only check when updating external projects (source != target)
        if [[ "$SCRIPT_DIR" != "$TARGET_DIR" ]]; then
            for ext in py sh md; do
                for f in "$SCRIPT_DIR/.claude/brain/"*."$ext"; do
                    [[ -f "$f" ]] || continue
                    local name
                    name=$(basename "$f")
                    check_pair "brain/$name" "$f" "$CLAUDE_DIR/brain/$name"
                done
            done
        fi
    fi
}

report_drift() {
    if [[ $DRIFT_COUNT -eq 0 ]]; then
        echo ""
        print_done "Zero drift. core/ e .claude/ estao sincronizados."
        return
    fi

    echo ""
    echo -e "${YELLOW}  Drift detectado em ${DRIFT_COUNT} arquivo(s) Layer 1:${NC}"
    echo ""

    local prev_group=""
    for i in "${!DRIFT_LABELS[@]}"; do
        local group
        group=$(echo "${DRIFT_LABELS[$i]}" | cut -d'/' -f1)
        if [[ "$group" != "$prev_group" ]]; then
            echo -e "  ${BOLD}$group/${NC}"
            prev_group="$group"
        fi
        echo -e "    ${YELLOW}•${NC} ${DRIFT_LABELS[$i]}"
    done
    echo ""
}

# ═══════════════════════════════════════════════════════════════
# UPDATE LAYERS
# ═══════════════════════════════════════════════════════════════

backup_before_update() {
    local BACKUP_DIR="$TARGET_DIR/.claude.bak"
    if [[ -d "$BACKUP_DIR" ]]; then
        rm -rf "$BACKUP_DIR"
    fi
    cp -r "$CLAUDE_DIR" "$BACKUP_DIR"
    print_done "Backup criado em .claude.bak/"
}

update_layer1() {
    print_step "Atualizando Layer 1 (CORE-OWNED)..."

    # ── Commands (overwrite) ──
    if [[ -d "$SCRIPT_DIR/core/commands" ]]; then
        cp "$SCRIPT_DIR/core/commands/"*.md "$CLAUDE_DIR/commands/" 2>/dev/null || true
        local cmd_count
        cmd_count=$(ls "$SCRIPT_DIR/core/commands/"*.md 2>/dev/null | wc -l | tr -d ' ')
        print_done "Commands atualizados ($cmd_count)"
    fi

    # ── DNA (overwrite) ──
    if [[ -d "$SCRIPT_DIR/core/dna" ]]; then
        cp -r "$SCRIPT_DIR/core/dna/"* "$CLAUDE_DIR/dna/" 2>/dev/null || true
        print_done "DNA/schemas atualizados"
    fi

    # ── Genesis (overwrite) ──
    if [[ -d "$SCRIPT_DIR/core/genesis" ]]; then
        mkdir -p "$CLAUDE_DIR/skills/engram-genesis"
        cp "$SCRIPT_DIR/core/genesis/SKILL.md" "$CLAUDE_DIR/skills/engram-genesis/" 2>/dev/null || true
        if [[ -d "$SCRIPT_DIR/core/genesis/scripts" ]]; then
            mkdir -p "$CLAUDE_DIR/skills/engram-genesis/scripts"
            cp "$SCRIPT_DIR/core/genesis/scripts/"* "$CLAUDE_DIR/skills/engram-genesis/scripts/" 2>/dev/null || true
            chmod +x "$CLAUDE_DIR/skills/engram-genesis/scripts/"*.py 2>/dev/null || true
        fi
        if [[ -d "$SCRIPT_DIR/core/genesis/references" ]]; then
            mkdir -p "$CLAUDE_DIR/skills/engram-genesis/references"
            cp "$SCRIPT_DIR/core/genesis/references/"* "$CLAUDE_DIR/skills/engram-genesis/references/" 2>/dev/null || true
        fi
        print_done "Genesis atualizado"
    fi

    # ── Evolution (overwrite) ──
    if [[ -d "$SCRIPT_DIR/core/evolution" ]]; then
        mkdir -p "$CLAUDE_DIR/skills/engram-evolution"
        cp "$SCRIPT_DIR/core/evolution/SKILL.md" "$CLAUDE_DIR/skills/engram-evolution/" 2>/dev/null || true
        if [[ -d "$SCRIPT_DIR/core/evolution/scripts" ]]; then
            mkdir -p "$CLAUDE_DIR/skills/engram-evolution/scripts"
            cp "$SCRIPT_DIR/core/evolution/scripts/"* "$CLAUDE_DIR/skills/engram-evolution/scripts/" 2>/dev/null || true
            chmod +x "$CLAUDE_DIR/skills/engram-evolution/scripts/"*.py 2>/dev/null || true
        fi
        print_done "Evolution atualizado"
    fi

    # ── Seeds (SKILL.md is CORE-OWNED, project files preserved) ──
    if [[ -d "$SCRIPT_DIR/core/seeds" ]]; then
        local seeds_new=0
        local seeds_updated=0
        for seed in "$SCRIPT_DIR/core/seeds"/*/; do
            [[ -d "$seed" ]] || continue
            local seed_name
            seed_name=$(basename "$seed")
            local dest="$CLAUDE_DIR/skills/$seed_name"
            if [[ ! -d "$dest" ]]; then
                # New seed — copy entire directory
                cp -r "${seed%/}" "$dest"
                seeds_new=$((seeds_new + 1))
            else
                # Existing seed — overwrite SKILL.md (core-owned)
                [[ -f "$seed/SKILL.md" ]] && cp "$seed/SKILL.md" "$dest/SKILL.md"
                seeds_updated=$((seeds_updated + 1))
            fi
        done
        [[ $seeds_new -gt 0 ]] && print_done "Seeds novos: $seeds_new"
        [[ $seeds_updated -gt 0 ]] && print_done "Seeds atualizados (SKILL.md): $seeds_updated"
    fi

    # ── Brain scripts (code only, never data) ──
    if [[ -d "$SCRIPT_DIR/.claude/brain" && -d "$CLAUDE_DIR/brain" ]]; then
        if [[ "$SCRIPT_DIR" != "$TARGET_DIR" ]]; then
            for ext in py sh md; do
                cp "$SCRIPT_DIR/.claude/brain/"*."$ext" "$CLAUDE_DIR/brain/" 2>/dev/null || true
            done
            chmod +x "$CLAUDE_DIR/brain/"*.py "$CLAUDE_DIR/brain/"*.sh 2>/dev/null || true
            print_done "Brain scripts atualizados (dados preservados)"
        else
            print_done "Brain scripts: self-hosted, skip (source = target)"
        fi
    fi

    # ── Brain venv ──
    if [[ -d "$CLAUDE_DIR/brain" ]]; then
        local VENV_DIR="$CLAUDE_DIR/brain/.venv"
        if [[ ! -d "$VENV_DIR" ]] || $FORCE; then
            if command -v python3 &>/dev/null; then
                print_step "Instalando/atualizando deps do Brain..."
                python3 -m venv "$VENV_DIR" 2>/dev/null || true
                "$VENV_DIR/bin/pip" install --quiet --upgrade pip 2>/dev/null || true
                "$VENV_DIR/bin/pip" install --quiet numpy sentence-transformers chromadb pydantic-settings 2>/dev/null || true
                print_done "Brain deps instaladas"
            else
                print_warn "Python3 nao encontrado — brain deps nao instaladas"
            fi
        else
            print_done "Brain deps: .venv existe (use --force para reinstalar)"
        fi
    fi
}

report_layer2() {
    echo ""
    print_step "Layer 2 (PROJECT-OWNED) — preservados:"
    [[ -d "$CLAUDE_DIR/agents" ]] && echo -e "    ${GREEN}✓${NC} agents/ ($(ls "$CLAUDE_DIR/agents/"*.md 2>/dev/null | wc -l | tr -d ' ') agents)"
    [[ -d "$CLAUDE_DIR/knowledge" ]] && echo -e "    ${GREEN}✓${NC} knowledge/"
    [[ -f "$TARGET_DIR/CLAUDE.md" ]] && echo -e "    ${GREEN}✓${NC} CLAUDE.md"
    [[ -f "$CLAUDE_DIR/settings.json" ]] && echo -e "    ${GREEN}✓${NC} settings.json"

    # Count project-owned skills (source != seed/core)
    local project_skills=0
    for skill_dir in "$CLAUDE_DIR/skills"/*/; do
        [[ -d "$skill_dir" ]] || continue
        local sname
        sname=$(basename "$skill_dir")
        # Skip core-owned skills
        [[ "$sname" == "engram-genesis" || "$sname" == "engram-evolution" ]] && continue
        [[ -d "$SCRIPT_DIR/core/seeds/$sname" ]] && continue
        project_skills=$((project_skills + 1))
    done
    [[ $project_skills -gt 0 ]] && echo -e "    ${GREEN}✓${NC} $project_skills skill(s) gerados pelo projeto"
}

report_layer3() {
    print_step "Layer 3 (RUNTIME) — intocados:"
    [[ -f "$CLAUDE_DIR/brain/brain.db" ]] && echo -e "    ${GREEN}✓${NC} brain/brain.db"
    [[ -f "$CLAUDE_DIR/manifest.json" ]] && echo -e "    ${GREEN}✓${NC} manifest.json"
    [[ -f "$CLAUDE_DIR/evolution-activations.json" ]] && echo -e "    ${GREEN}✓${NC} evolution-activations.json"
}

update_manifest() {
    if [[ ! -f "$CLAUDE_DIR/manifest.json" ]]; then
        return
    fi

    python3 - "$CLAUDE_DIR/manifest.json" "$VERSION" "$SCRIPT_DIR" << 'PYEOF'
import json, sys, os
from datetime import datetime

manifest_path = sys.argv[1]
version = sys.argv[2]
script_dir = sys.argv[3]

with open(manifest_path, 'r') as f:
    manifest = json.load(f)

manifest['engram_version'] = version
manifest['last_updated'] = datetime.now().astimezone().isoformat()

seeds_dir = os.path.join(script_dir, 'core', 'seeds')
if os.path.isdir(seeds_dir):
    existing_skills = manifest.get('components', {}).get('skills', {})
    for seed_name in os.listdir(seeds_dir):
        seed_path = os.path.join(seeds_dir, seed_name)
        if os.path.isdir(seed_path) and seed_name not in existing_skills:
            existing_skills[seed_name] = {
                "version": "1.0.0",
                "source": "seed",
                "created_at": datetime.now().astimezone().isoformat(),
                "updated_at": datetime.now().astimezone().isoformat(),
                "activations": 0,
                "last_used": None,
                "health": "active"
            }
    manifest.setdefault('components', {})['skills'] = existing_skills

with open(manifest_path, 'w') as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)
    f.write('\n')
PYEOF
    print_done "manifest.json: version atualizada para v${VERSION}"
}

update_version() {
    echo "$VERSION" > "$CLAUDE_DIR/.engram-version"
    print_done "Versao atualizada: v${VERSION}"
}

handle_regenerate() {
    if ! $REGENERATE; then
        return
    fi

    echo ""
    print_step "Regenerando CLAUDE.md e settings.json..."
    [[ -f "$TARGET_DIR/CLAUDE.md" ]] && cp "$TARGET_DIR/CLAUDE.md" "$TARGET_DIR/CLAUDE.md.pre-update.bak"
    [[ -f "$CLAUDE_DIR/settings.json" ]] && cp "$CLAUDE_DIR/settings.json" "$CLAUDE_DIR/settings.json.pre-update.bak"

    # Delegate to setup.sh --update for regeneration (it has detect_stack + generate_claude_md)
    if [[ -f "$SCRIPT_DIR/setup.sh" ]]; then
        bash "$SCRIPT_DIR/setup.sh" --update "$TARGET_DIR"
        print_done "CLAUDE.md e settings.json regenerados (backup em .pre-update.bak)"
    else
        print_err "setup.sh nao encontrado — nao foi possivel regenerar"
    fi
}

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

main() {
    preflight
    detect_drift
    report_drift

    # Check-only mode
    if [[ "$MODE" == "check" ]]; then
        [[ $DRIFT_COUNT -eq 0 ]] && exit 0 || exit 1
    fi

    # Confirmation
    if [[ $DRIFT_COUNT -gt 0 ]] && ! $FORCE; then
        echo -e "  ${BOLD}Layer 1 sera atualizado de core/ (${DRIFT_COUNT} arquivo(s) alterados).${NC}"
        echo -e "  Layer 2 e Layer 3 serao preservados."
        echo ""
        read -p "  Continuar? (S/n): " -n 1 -r
        echo ""
        [[ $REPLY =~ ^[Nn]$ ]] && echo "  Cancelado." && exit 0
    elif [[ $DRIFT_COUNT -eq 0 ]]; then
        echo -e "  Nenhuma atualizacao necessaria."
        echo ""
        read -p "  Forcar update mesmo assim? (s/N): " -n 1 -r
        echo ""
        [[ ! $REPLY =~ ^[Ss]$ ]] && echo "  OK." && exit 0
    fi

    echo ""
    backup_before_update
    echo ""
    update_layer1
    report_layer2
    echo ""
    report_layer3
    echo ""
    update_manifest
    update_version
    handle_regenerate

    # ── Final report ──
    echo ""
    echo -e "${BOLD}═══════════════════════════════════════${NC}"
    echo -e "${GREEN}  Update concluido (v${VERSION})${NC}"
    echo -e "${BOLD}═══════════════════════════════════════${NC}"
    echo ""
    echo -e "  Proximo passo: rode ${BOLD}/init-engram${NC} se for a primeira vez,"
    echo -e "  ou ${BOLD}/doctor${NC} para verificar saude."
    echo ""
}

main
