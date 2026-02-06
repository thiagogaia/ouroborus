#!/usr/bin/env python3
"""
migrate_to_sqlite.py - Migrate brain from graph.json to SQLite + FTS5 (Schema v2)

Reads graph.json, creates brain.db with v2 schema (hybrid property graph
with generated columns, normalized labels, multi-edge support), inserts
nodes and edges in batch, rebuilds FTS5 index, and verifies counts.

Also handles in-place migration from schema v1 to v2.

Usage:
    python3 migrate_to_sqlite.py                 # Migrate
    python3 migrate_to_sqlite.py --verify        # Migrate + spot-check
    python3 migrate_to_sqlite.py --dry-run       # Show what would happen
"""

import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from brain_sqlite import BrainSQLite, SCHEMA_SQL, FTS_SCHEMA_SQL, SCHEMA_VERSION


def migrate(base_path: Path = None, verify: bool = False, dry_run: bool = False) -> dict:
    """Migrate graph.json to brain.db (schema v2).

    Args:
        base_path: Path to .claude/brain/ directory
        verify: If True, do spot-checks after migration
        dry_run: If True, show stats without writing

    Returns:
        Dict with migration statistics
    """
    if base_path is None:
        base_path = Path(".claude/brain")
    base_path = Path(base_path)

    graph_file = base_path / "graph.json"
    db_file = base_path / "brain.db"

    if not graph_file.exists():
        print(f"Error: {graph_file} not found")
        return {"error": "graph.json not found"}

    # Load JSON
    print(f"Reading {graph_file}...")
    data = json.loads(graph_file.read_text(encoding='utf-8'))
    nodes = data.get("nodes", {})
    edges = data.get("edges", [])

    print(f"Found {len(nodes)} nodes, {len(edges)} edges")

    if dry_run:
        print("Dry run — not writing to disk")
        return {"nodes": len(nodes), "edges": len(edges), "dry_run": True}

    # Remove existing DB if present (fresh migration)
    if db_file.exists():
        print(f"Removing existing {db_file}...")
        db_file.unlink()

    # Create DB with v2 schema
    print(f"Creating {db_file} (schema v2)...")
    conn = sqlite3.connect(str(db_file))
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA_SQL)

    # Create FTS table
    has_fts = True
    try:
        conn.executescript(FTS_SCHEMA_SQL)
    except sqlite3.OperationalError as e:
        print(f"Warning: FTS5 not available ({e}). Full-text search will use fallback.")
        has_fts = False

    conn.commit()

    # Insert nodes in batch
    print("Inserting nodes...")
    node_count = 0
    node_errors = 0

    conn.execute("BEGIN TRANSACTION")
    for node_id, node_data in nodes.items():
        try:
            labels = node_data.get("labels", [])
            props = node_data.get("props", {})
            memory = node_data.get("memory", {})

            # Build unified properties JSON blob
            properties = {
                "title": props.get("title", ""),
                "author": props.get("author", ""),
                "content": props.get("content", ""),
                "summary": props.get("summary", ""),
                "strength": memory.get("strength", 1.0),
                "access_count": memory.get("access_count", 0),
                "last_accessed": memory.get("last_accessed", datetime.now().isoformat()),
                "created_at": memory.get("created_at", datetime.now().isoformat()),
                "decay_rate": memory.get("decay_rate", 0.02),
            }
            # Add extra props (everything except core fields)
            for k, v in props.items():
                if k not in ("title", "author", "content", "summary"):
                    properties[k] = v

            conn.execute(
                "INSERT INTO nodes (id, properties) VALUES (?, ?)",
                (node_id, json.dumps(properties, default=str))
            )

            # Insert labels into node_labels table
            for label in labels:
                conn.execute(
                    "INSERT OR IGNORE INTO node_labels (node_id, label) VALUES (?, ?)",
                    (node_id, label)
                )

            node_count += 1
        except Exception as e:
            print(f"  Error inserting node {node_id}: {e}")
            node_errors += 1

    conn.execute("COMMIT")
    print(f"  Inserted {node_count} nodes ({node_errors} errors)")

    # Insert edges in batch (with multi-edge support)
    print("Inserting edges...")
    edge_count = 0
    edge_errors = 0
    edge_skipped = 0

    conn.execute("BEGIN TRANSACTION")
    for edge in edges:
        try:
            src = edge.get("src", "")
            tgt = edge.get("tgt", "")

            # Verify both endpoints exist
            src_exists = conn.execute("SELECT 1 FROM nodes WHERE id = ?", (src,)).fetchone()
            tgt_exists = conn.execute("SELECT 1 FROM nodes WHERE id = ?", (tgt,)).fetchone()
            if not src_exists or not tgt_exists:
                edge_skipped += 1
                continue

            conn.execute(
                """INSERT INTO edges (from_id, to_id, type, weight, properties, created_at)
                   VALUES (?, ?, ?, ?, ?, ?)
                   ON CONFLICT(from_id, to_id, type) DO UPDATE SET
                       weight = MAX(weight, excluded.weight)""",
                (src, tgt,
                 edge.get("type", "REFERENCES"),
                 edge.get("weight", 0.5),
                 json.dumps(edge.get("props", {}), default=str),
                 edge.get("created_at"))
            )
            edge_count += 1
        except Exception as e:
            print(f"  Error inserting edge {src}->{tgt}: {e}")
            edge_errors += 1

    conn.execute("COMMIT")
    print(f"  Inserted {edge_count} edges ({edge_errors} errors, {edge_skipped} skipped)")

    # Rebuild FTS index
    if has_fts:
        print("Rebuilding FTS5 index...")
        try:
            conn.execute("INSERT INTO nodes_fts(nodes_fts) VALUES('rebuild')")
            conn.commit()
            print("  FTS5 index rebuilt")
        except sqlite3.OperationalError as e:
            print(f"  FTS5 rebuild failed: {e}")

    # Store metadata
    conn.execute(
        "INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?)",
        ("schema_version", SCHEMA_VERSION)
    )
    conn.execute(
        "INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?)",
        ("migrated_at", datetime.now().isoformat())
    )
    conn.execute(
        "INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?)",
        ("source", str(graph_file))
    )
    conn.commit()

    # Verify
    result = {
        "nodes_json": len(nodes),
        "edges_json": len(edges),
        "nodes_db": node_count,
        "edges_db": edge_count,
        "node_errors": node_errors,
        "edge_errors": edge_errors,
        "edge_skipped": edge_skipped,
        "has_fts": has_fts,
        "schema_version": SCHEMA_VERSION,
    }

    if verify:
        print("\n=== Verification ===")
        result["verify"] = _verify(conn, nodes, edges)

    # Report DB size
    conn.close()
    db_size = db_file.stat().st_size
    json_size = graph_file.stat().st_size
    result["db_size_kb"] = round(db_size / 1024, 1)
    result["json_size_kb"] = round(json_size / 1024, 1)

    print(f"\nMigration complete (schema v{SCHEMA_VERSION}):")
    print(f"  graph.json: {result['json_size_kb']} KB")
    print(f"  brain.db:   {result['db_size_kb']} KB")
    print(f"  Nodes: {node_count}/{len(nodes)}")
    print(f"  Edges: {edge_count}/{len(edges)}")

    return result


def _verify(conn: sqlite3.Connection, nodes: dict, edges: list) -> dict:
    """Spot-check migration accuracy."""
    checks = {"passed": 0, "failed": 0, "details": []}

    # Check node count
    db_count = conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
    if db_count == len(nodes):
        checks["passed"] += 1
        checks["details"].append(f"Node count matches: {db_count}")
    else:
        checks["failed"] += 1
        checks["details"].append(f"Node count mismatch: DB={db_count} JSON={len(nodes)}")

    # Check edge count (may be >= because multi-edge now preserves by type)
    db_edge_count = conn.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
    checks["details"].append(f"  Edge count: DB={db_edge_count} JSON={len(edges)}")

    # Check node_labels count
    label_count = conn.execute("SELECT COUNT(*) FROM node_labels").fetchone()[0]
    checks["details"].append(f"  Label entries: {label_count}")

    # Spot-check 5 random nodes
    import random
    sample_ids = random.sample(list(nodes.keys()), min(5, len(nodes)))

    for nid in sample_ids:
        json_node = nodes[nid]
        row = conn.execute("SELECT * FROM nodes WHERE id = ?", (nid,)).fetchone()

        if row is None:
            checks["failed"] += 1
            checks["details"].append(f"Node {nid} not found in DB")
            continue

        # Check title (via generated column)
        json_title = json_node.get("props", {}).get("title", "")
        if row["title"] == json_title:
            checks["passed"] += 1
        else:
            checks["failed"] += 1
            checks["details"].append(f"Node {nid} title mismatch: DB='{row['title']}' JSON='{json_title}'")

        # Check labels (from node_labels table)
        json_labels = set(json_node.get("labels", []))
        db_labels_rows = conn.execute(
            "SELECT label FROM node_labels WHERE node_id = ?", (nid,)
        ).fetchall()
        db_labels = set(r["label"] for r in db_labels_rows)
        if json_labels == db_labels:
            checks["passed"] += 1
        else:
            checks["failed"] += 1
            checks["details"].append(f"Node {nid} labels mismatch: DB={db_labels} JSON={json_labels}")

        # Check strength (via generated column)
        json_strength = json_node.get("memory", {}).get("strength", 1.0)
        if abs(row["strength"] - json_strength) < 0.001:
            checks["passed"] += 1
        else:
            checks["failed"] += 1
            checks["details"].append(f"Node {nid} strength mismatch: DB={row['strength']} JSON={json_strength}")

    # Check schema version
    version_row = conn.execute(
        "SELECT value FROM meta WHERE key = 'schema_version'"
    ).fetchone()
    if version_row and version_row[0] == SCHEMA_VERSION:
        checks["passed"] += 1
        checks["details"].append(f"Schema version: {version_row[0]}")
    else:
        checks["failed"] += 1
        checks["details"].append(f"Schema version mismatch: expected {SCHEMA_VERSION}")

    for detail in checks["details"]:
        print(f"  {detail}")

    print(f"\n  Passed: {checks['passed']}, Failed: {checks['failed']}")
    return checks


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Migrate brain from JSON to SQLite (schema v2)")
    parser.add_argument("--verify", action="store_true", help="Run spot-checks after migration")
    parser.add_argument("--dry-run", action="store_true", help="Show stats without writing")
    parser.add_argument("--path", type=str, default=".claude/brain", help="Path to brain directory")
    args = parser.parse_args()

    result = migrate(
        base_path=Path(args.path),
        verify=args.verify,
        dry_run=args.dry_run
    )
    print(json.dumps(result, indent=2))
