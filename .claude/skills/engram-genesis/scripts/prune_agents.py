#!/usr/bin/env python3
"""
Engram Genesis — Prune Agents
Removes agents that are not needed for the project.

Usage:
    python3 prune_agents.py --project-dir . --remove db-expert,auth-expert --output json
    python3 prune_agents.py --project-dir . --needed architect,domain-analyst --output json
    python3 prune_agents.py --project-dir . --needed architect,domain-analyst --dry-run
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent


def list_existing_agents(project_dir: str) -> list:
    """List agents in .claude/agents/ (stem = name)."""
    agents_dir = Path(project_dir) / ".claude" / "agents"
    if not agents_dir.is_dir():
        return []
    return [f.stem for f in agents_dir.glob("*.md")]


def parse_list_arg(value: str) -> set:
    """Parse comma or space separated list into set of names."""
    if not value or not value.strip():
        return set()
    names = []
    for part in value.replace(",", " ").split():
        name = part.strip()
        if name:
            names.append(name)
    return set(names)


def _call_unregister(project_dir: str, name: str, quiet: bool = False) -> bool:
    """Call register.py --unregister. Returns True on success."""
    register_script = SCRIPT_DIR / "register.py"
    cmd = [
        sys.executable,
        str(register_script),
        "--unregister",
        "--type", "agent",
        "--name", name,
        "--project-dir", project_dir,
    ]
    try:
        result = subprocess.run(
            cmd,
            capture_output=quiet,
            cwd=project_dir,
            check=False,
        )
        return result.returncode == 0
    except Exception:
        return False


def run_prune(project_dir: str, to_remove: set, dry_run: bool = False, quiet: bool = False) -> dict:
    """
    Remove agents in to_remove: delete file and unregister.
    Returns {"removed": [...], "errors": [...]}.
    """
    agents_dir = Path(project_dir) / ".claude" / "agents"
    removed = []
    errors = []

    for name in sorted(to_remove):
        agent_file = agents_dir / f"{name}.md"

        if not agent_file.exists():
            if not dry_run:
                if not _call_unregister(project_dir, name, quiet):
                    errors.append({"agent": name, "error": "Unregister failed"})
            continue

        if dry_run:
            removed.append(name)
            continue

        try:
            agent_file.unlink()
            removed.append(name)
        except OSError as e:
            errors.append({"agent": name, "error": f"Failed to delete: {e}"})
            continue

        if not _call_unregister(project_dir, name, quiet):
            errors.append({"agent": name, "error": "Unregister failed"})

    return {"removed": removed, "errors": errors}


def main():
    parser = argparse.ArgumentParser(
        description="Engram — Prune agents not needed for the project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Remove specific agents
  python3 prune_agents.py --project-dir . --remove db-expert,auth-expert

  # Keep only needed agents (remove the rest)
  python3 prune_agents.py --project-dir . --needed architect,domain-analyst

  # Dry-run (report only, no changes)
  python3 prune_agents.py --project-dir . --needed architect --dry-run
        """,
    )
    parser.add_argument("--project-dir", default=".", help="Project root directory")
    parser.add_argument(
        "--remove",
        metavar="LIST",
        help="Comma-separated list of agents to remove (e.g. db-expert,auth-expert)",
    )
    parser.add_argument(
        "--needed",
        metavar="LIST",
        help="Comma-separated list of agents to keep (removes existing - needed)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Report only, do not delete")
    parser.add_argument("--output", choices=["text", "json"], default="text")

    args = parser.parse_args()
    project_dir = os.path.abspath(args.project_dir)

    if not args.remove and not args.needed:
        parser.error("Must specify --remove or --needed")

    existing = set(list_existing_agents(project_dir))

    if args.remove:
        to_remove = parse_list_arg(args.remove) & existing
    else:
        needed = parse_list_arg(args.needed)
        to_remove = existing - needed

    result = run_prune(project_dir, to_remove, dry_run=args.dry_run, quiet=(args.output == "json"))

    if args.output == "json":
        output = {
            "removed": result["removed"],
            "errors": result["errors"],
            "dry_run": args.dry_run,
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        if args.dry_run:
            print("\n🔍 Dry-run — nenhuma alteração feita\n")
        if result["removed"]:
            print(f"  Removidos: {', '.join(result['removed'])}")
        if result["errors"]:
            for err in result["errors"]:
                print(f"  ⚠️  {err['agent']}: {err['error']}")
        if not result["removed"] and not result["errors"]:
            print("  Nenhum agent removido.")


if __name__ == "__main__":
    main()
