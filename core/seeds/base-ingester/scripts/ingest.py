#!/usr/bin/env python3
"""
Engram Base Ingester — Bulk documentation import into the organizational brain.

Reads a directory of .md files, extracts structured knowledge (entities, services,
rules, endpoints), creates typed nodes and automatic edges in the brain graph.

Usage:
    python3 ingest.py --source /path/to/docs --project-dir .
    python3 ingest.py --source /path/to/docs --project-dir . --type domain --dry-run
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def get_brain_path(project_dir: str) -> Path:
    """Resolve brain path from project root."""
    return Path(project_dir) / ".claude" / "brain"


def get_author() -> str:
    """Get current developer identity from git."""
    try:
        email = subprocess.check_output(
            ["git", "config", "user.email"],
            text=True, stderr=subprocess.DEVNULL
        ).strip()
        username = re.sub(r'[^a-z0-9]', '-', email.split("@")[0].lower())
        return f"@{username}"
    except Exception:
        import getpass
        return f"@{getpass.getuser()}"


def content_hash(content: str) -> str:
    """Generate short hash for idempotency check."""
    return hashlib.sha256(content.encode()).hexdigest()[:12]


def parse_markdown(filepath: Path) -> Dict:
    """Parse a markdown file and extract structured information."""
    text = filepath.read_text(encoding="utf-8")
    result = {
        "filepath": str(filepath),
        "filename": filepath.stem,
        "content": text,
        "hash": content_hash(text),
        "title": None,
        "description": None,
        "headers": [],
        "tables": [],
        "services": [],
        "entities": [],
        "endpoints": [],
        "references": [],
    }

    lines = text.split("\n")

    # Extract title (first H1)
    for line in lines:
        if line.startswith("# ") and not line.startswith("##"):
            result["title"] = line[2:].strip()
            break

    if not result["title"]:
        result["title"] = filepath.stem.replace("-", " ").replace("_", " ").title()

    # Extract description (first non-empty paragraph after title)
    in_description = False
    desc_lines = []
    for line in lines:
        if line.startswith("# ") and not in_description:
            in_description = True
            continue
        if in_description:
            if line.strip() == "":
                if desc_lines:
                    break
                continue
            if line.startswith("#") or line.startswith("|") or line.startswith("```"):
                break
            desc_lines.append(line.strip())

    result["description"] = " ".join(desc_lines)[:300] if desc_lines else ""

    # Extract headers (H2, H3)
    for line in lines:
        if line.startswith("## "):
            result["headers"].append({"level": 2, "text": line[3:].strip()})
        elif line.startswith("### "):
            result["headers"].append({"level": 3, "text": line[4:].strip()})

    # Extract tables
    current_table = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            cells = [c.strip() for c in stripped.split("|")[1:-1]]
            if current_table is None:
                # Header row
                current_table = {"headers": cells, "rows": [], "line": i}
            elif all(c.replace("-", "").replace(":", "").strip() == "" for c in cells):
                # Separator row, skip
                continue
            else:
                current_table["rows"].append(cells)
        else:
            if current_table and current_table["rows"]:
                result["tables"].append(current_table)
            current_table = None

    if current_table and current_table["rows"]:
        result["tables"].append(current_table)

    # Extract services from tables
    for table in result["tables"]:
        headers_lower = [h.lower() for h in table["headers"]]
        svc_col = None
        for i, h in enumerate(headers_lower):
            if h in ("serviço", "servico", "service", "nome", "name", "repo"):
                svc_col = i
                break

        if svc_col is not None:
            desc_col = next(
                (i for i, h in enumerate(headers_lower)
                 if h in ("descrição", "descricao", "description", "desc")),
                None
            )
            stack_col = next(
                (i for i, h in enumerate(headers_lower)
                 if h in ("stack", "tech", "tecnologia")),
                None
            )

            for row in table["rows"]:
                if svc_col < len(row) and row[svc_col].strip():
                    svc_name = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', row[svc_col].strip())
                    svc_name = re.sub(r'[*_`]', '', svc_name).strip()
                    if svc_name and len(svc_name) > 1:
                        svc = {"name": svc_name}
                        if desc_col is not None and desc_col < len(row):
                            svc["description"] = row[desc_col].strip()
                        if stack_col is not None and stack_col < len(row):
                            svc["stack"] = row[stack_col].strip()
                        result["services"].append(svc)

    # Extract entities from hierarchy patterns (trees like A → B → C)
    for line in lines:
        arrow_match = re.findall(r'(\w[\w\s]+?)\s*[→←↔]\s*', line)
        if arrow_match:
            for entity in arrow_match:
                entity = entity.strip()
                if len(entity) > 2 and not entity.startswith(("http", "//", "#")):
                    result["entities"].append(entity)

    # Extract references to other files
    md_links = re.findall(r'\[(?:[^\]]+)\]\(([^)]+\.md)\)', text)
    for link in md_links:
        result["references"].append(link)

    # Extract inline references to service names
    backtick_refs = re.findall(r'`([a-z][\w-]+)`', text)
    result["inline_refs"] = [r for r in backtick_refs if len(r) > 2]

    return result


def get_labels_for_type(base_type: str, parsed: Dict) -> List[str]:
    """Determine node labels based on base type and content."""
    if base_type == "domain":
        return ["Concept", "Domain"]
    elif base_type == "infra":
        return ["Concept", "Infrastructure"]
    elif base_type == "services":
        return ["Concept", "Service"]
    else:
        return ["Concept"]


def get_decay_for_type(base_type: str) -> float:
    """Get decay rate by base type."""
    rates = {
        "domain": 0.003,
        "infra": 0.005,
        "services": 0.003,
        "mixed": 0.005,
    }
    return rates.get(base_type, 0.005)


def ingest(
    source_dir: str,
    project_dir: str,
    base_type: str = "mixed",
    author: str = None,
    dry_run: bool = False
) -> Dict:
    """
    Main ingestion function.

    Returns stats dict with counts of created nodes/edges.
    """
    source = Path(source_dir).resolve()
    project = Path(project_dir).resolve()
    brain_path = get_brain_path(project_dir)

    if not source.is_dir():
        print(f"Error: Source directory not found: {source}")
        sys.exit(1)

    if not brain_path.exists():
        print(f"Error: Brain not found at {brain_path}. Run setup.sh first.")
        sys.exit(1)

    # Add brain to sys.path for import
    sys.path.insert(0, str(brain_path))
    from brain import Brain, get_current_developer

    if author is None:
        author = get_author()

    # Load brain
    brain = Brain(brain_path)
    brain.load()

    # Collect existing hashes for idempotency
    existing_hashes = set()
    nodes_iter = brain.graph.nodes if hasattr(brain.graph, 'nodes') and not callable(brain.graph.nodes) else brain.graph._nodes
    for node_id in nodes_iter:
        node = brain.graph.nodes[node_id] if hasattr(brain.graph.nodes, '__getitem__') else brain.graph._nodes[node_id]
        props = node.get("props", {})
        if props.get("source_hash"):
            existing_hashes.add(props["source_hash"])

    # Find all .md files
    md_files = sorted(source.rglob("*.md"))

    if not md_files:
        print(f"No .md files found in {source}")
        return {"files": 0, "nodes": 0, "edges": 0, "skipped": 0}

    print(f"\nFound {len(md_files)} markdown files in {source}")
    print(f"Type: {base_type} | Author: {author}")
    print("=" * 60)

    # Parse all files
    parsed_files = []
    for f in md_files:
        try:
            parsed = parse_markdown(f)
            parsed_files.append(parsed)
        except Exception as e:
            print(f"  Warning: Failed to parse {f.name}: {e}")

    # Stats
    stats = {
        "files": len(parsed_files),
        "nodes_created": 0,
        "edges_created": 0,
        "services_found": 0,
        "entities_found": 0,
        "skipped": 0,
    }

    # Count totals for dry run
    total_services = sum(len(p["services"]) for p in parsed_files)
    stats["services_found"] = total_services
    stats["entities_found"] = sum(len(p["entities"]) for p in parsed_files)

    if dry_run:
        print(f"\n{'DRY RUN':=^60}")
        print(f"  Files to process:  {stats['files']}")
        print(f"  Document nodes:    {stats['files']}")
        print(f"  Service nodes:     {stats['services_found']}")
        print(f"  Entity mentions:   {stats['entities_found']}")
        est_nodes = stats["files"] + total_services
        est_edges = stats["files"] * 2 + total_services  # domain + author + refs
        print(f"  Estimated nodes:   ~{est_nodes}")
        print(f"  Estimated edges:   ~{est_edges}")
        print(f"{'':=^60}")

        for p in parsed_files:
            status = "SKIP" if p["hash"] in existing_hashes else "NEW"
            print(f"  [{status}] {p['title']}")
            for svc in p["services"][:5]:
                print(f"        -> Service: {svc['name']}")
            if len(p["services"]) > 5:
                print(f"        -> ... and {len(p['services']) - 5} more")

        return stats

    # ── Create nodes ───────────────────────────────────────

    # Track created node IDs by name for cross-referencing
    node_map = {}  # filename/service_name -> node_id

    # Ensure domain node exists
    domain_id = brain._ensure_domain_node(base_type)

    for parsed in parsed_files:
        # Skip if already ingested (idempotency)
        if parsed["hash"] in existing_hashes:
            stats["skipped"] += 1
            print(f"  [SKIP] {parsed['title']} (already ingested)")
            continue

        # Create document node
        labels = get_labels_for_type(base_type, parsed)
        node_id = brain.add_memory(
            title=parsed["title"],
            content=parsed["content"],
            labels=labels,
            author=author,
            props={
                "source_hash": parsed["hash"],
                "source_file": parsed["filepath"],
                "description": parsed["description"],
                "ingested_from": str(source),
                "base_type": base_type,
            },
        )
        node_map[parsed["filename"]] = node_id
        stats["nodes_created"] += 1
        print(f"  [NEW] {parsed['title']} -> {node_id}")

        # Connect to domain
        brain.add_edge(node_id, domain_id, "BELONGS_TO", weight=0.6)
        stats["edges_created"] += 1

        # Create service nodes from tables
        for svc in parsed["services"]:
            svc_slug = re.sub(r'[^a-z0-9]+', '-', svc["name"].lower())
            svc_key = f"svc-{svc_slug}"

            if svc_key not in node_map:
                svc_node_id = brain.add_memory(
                    title=svc["name"],
                    content=svc.get("description", f"Service: {svc['name']}"),
                    labels=["Service", "Concept"],
                    author=author,
                    props={
                        "source_hash": content_hash(svc["name"]),
                        "stack": svc.get("stack", ""),
                        "ingested_from": str(source),
                        "base_type": base_type,
                    },
                )
                node_map[svc_key] = svc_node_id
                stats["nodes_created"] += 1
                print(f"        -> Service: {svc['name']} -> {svc_node_id}")

                # Connect service to domain
                brain.add_edge(svc_node_id, domain_id, "BELONGS_TO", weight=0.7)
                stats["edges_created"] += 1

            # Connect document to service
            brain.add_edge(node_id, node_map[svc_key], "CONTAINS", weight=0.8)
            stats["edges_created"] += 1

    # ── Create cross-reference edges ──────────────────────

    for parsed in parsed_files:
        src_id = node_map.get(parsed["filename"])
        if not src_id:
            continue

        # File references (links to other .md files)
        for ref in parsed["references"]:
            ref_name = Path(ref).stem
            tgt_id = node_map.get(ref_name)
            if tgt_id and tgt_id != src_id:
                brain.add_edge(src_id, tgt_id, "REFERENCES", weight=0.6)
                stats["edges_created"] += 1

        # Inline references (backtick mentions of services)
        for ref in parsed.get("inline_refs", []):
            ref_slug = f"svc-{ref}"
            tgt_id = node_map.get(ref_slug)
            if tgt_id and tgt_id != src_id:
                brain.add_edge(src_id, tgt_id, "REFERENCES", weight=0.4)
                stats["edges_created"] += 1

    # ── Create inter-service dependency edges ─────────────

    # If a service doc mentions another service by name, create DEPENDS_ON
    service_names = {k: v for k, v in node_map.items() if k.startswith("svc-")}
    for parsed in parsed_files:
        src_services = [
            f"svc-{re.sub(r'[^a-z0-9]+', '-', s['name'].lower())}"
            for s in parsed["services"]
        ]
        content_lower = parsed["content"].lower()

        for svc_key, svc_id in service_names.items():
            svc_name = svc_key.replace("svc-", "").replace("-", " ")
            # Check if this service is mentioned in this doc
            # but is not defined in this doc's own tables
            if svc_key not in src_services and svc_name in content_lower:
                doc_id = node_map.get(parsed["filename"])
                if doc_id and doc_id != svc_id:
                    brain.add_edge(doc_id, svc_id, "REFERENCES", weight=0.3)
                    stats["edges_created"] += 1

    # Save
    brain.save()

    # Print summary
    print(f"\n{'SUMMARY':=^60}")
    print(f"  Files processed:   {stats['files']}")
    print(f"  Skipped (dup):     {stats['skipped']}")
    print(f"  Nodes created:     {stats['nodes_created']}")
    print(f"  Edges created:     {stats['edges_created']}")
    print(f"  Services found:    {stats['services_found']}")

    brain_stats = brain.get_stats()
    print(f"\n  Brain total:       {brain_stats['nodes']} nodes, {brain_stats['edges']} edges")
    print(f"  Embeddings:        {brain_stats['embeddings']} (run embeddings.py build to update)")
    print(f"{'':=^60}")

    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Engram Base Ingester — Bulk documentation import"
    )
    parser.add_argument(
        "--source", required=True,
        help="Path to directory with .md files to ingest"
    )
    parser.add_argument(
        "--project-dir", default=".",
        help="Project root with Engram installed (default: .)"
    )
    parser.add_argument(
        "--type", choices=["domain", "infra", "services", "mixed"],
        default="mixed",
        help="Type of knowledge base (default: mixed)"
    )
    parser.add_argument(
        "--author",
        help="Author of the memories (default: git user)"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would be created without executing"
    )

    args = parser.parse_args()

    ingest(
        source_dir=args.source,
        project_dir=args.project_dir,
        base_type=args.type,
        author=args.author,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
