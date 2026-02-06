"""Shared fixtures for brain tests.

Blocks networkx, numpy, and sentence_transformers BEFORE any brain import
to guarantee all tests use FallbackGraph.
"""

import sys
import types
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pytest

# ── Block heavy deps so FallbackGraph is always used ──
_BLOCKED = ("networkx", "nx", "sentence_transformers")


@pytest.fixture(autouse=True, scope="session")
def _block_heavy_deps():
    """Block networkx/numpy/sentence_transformers for the entire test session.

    numpy is replaced with a MagicMock that exposes the attrs brain.py/embeddings.py
    need at import time (ndarray, array, dot, linalg.norm) so the modules can be
    imported without sys.exit().
    """
    saved = {}

    # Block networkx and sentence_transformers
    for mod_name in _BLOCKED:
        saved[mod_name] = sys.modules.get(mod_name)
        sys.modules[mod_name] = None  # type: ignore[assignment]

    # Block numpy with a mock that prevents sys.exit in embeddings.py
    np_mock = MagicMock()
    np_mock.__name__ = "numpy"
    np_mock.ndarray = list
    np_mock.array = lambda x: list(x) if hasattr(x, '__iter__') else [x]
    np_mock.dot = lambda a, b: sum(x * y for x, y in zip(a, b))
    linalg_mock = MagicMock()
    linalg_mock.norm = lambda v, **kw: sum(x * x for x in v) ** 0.5
    np_mock.linalg = linalg_mock
    saved["numpy"] = sys.modules.get("numpy")
    saved["np"] = sys.modules.get("np")
    sys.modules["numpy"] = np_mock

    yield

    # Restore
    for mod_name, original in saved.items():
        if original is None:
            sys.modules.pop(mod_name, None)
        else:
            sys.modules[mod_name] = original


# ── Path setup ──
BRAIN_DIR = Path(__file__).resolve().parent.parent.parent / ".claude" / "brain"
FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


@pytest.fixture(autouse=True, scope="session")
def _add_brain_to_path():
    """Add .claude/brain/ to sys.path so we can import brain, sleep, etc."""
    brain_str = str(BRAIN_DIR)
    if brain_str not in sys.path:
        sys.path.insert(0, brain_str)
    yield


# ── Brain fixtures ──


@pytest.fixture
def empty_brain(tmp_path):
    """A fresh Brain with no nodes, base_path pointing to tmp_path."""
    from brain import Brain
    b = Brain(base_path=tmp_path / "brain")
    return b


@pytest.fixture
def seeded_brain(tmp_path):
    """Brain pre-populated with 7 nodes and various edges.

    Nodes:
      - adr1: ADR/Decision  (title: "ADR-001: Use FallbackGraph")
      - adr2: ADR/Decision  (title: "ADR-002: Deterministic IDs")
      - pat1: Pattern/ApprovedPattern (title: "PAT-001: Feedback Loop")
      - pat2: Pattern/ApprovedPattern (title: "PAT-002: Dedup Strategy")
      - commit1: Episode/Commit (title: "feat(brain): add fallback graph")
      - concept1: Concept (title: "Engram Memory System")
      - person1: Person (person-test@dev.com)

    Edges:
      adr1 -> person1  AUTHORED_BY
      adr2 -> person1  AUTHORED_BY
      pat1 -> person1  AUTHORED_BY
      pat1 -> adr1     REFERENCES  (pattern references ADR)
      commit1 -> person1  AUTHORED_BY
      commit1 -> pat1   APPLIES     (commit applies pattern)
      concept1 -> person1  AUTHORED_BY
    """
    from brain import Brain

    b = Brain(base_path=tmp_path / "brain")
    now = datetime.now().isoformat()
    recent = (datetime.now() - timedelta(days=1)).isoformat()

    # Helper to add node directly (bypass add_memory to have deterministic IDs)
    def _add(node_id, labels, title, content="", extra_props=None, strength=1.0, access_count=1):
        props = {"title": title, "content": content, "summary": content[:200], "author": "test@dev.com"}
        if extra_props:
            props.update(extra_props)
        b.graph.add_node(
            node_id,
            labels=labels,
            props=props,
            memory={
                "strength": strength,
                "access_count": access_count,
                "last_accessed": now,
                "created_at": recent,
                "decay_rate": 0.01,
            },
        )

    _add("adr1", ["Decision", "ADR"], "ADR-001: Use FallbackGraph",
         "NetworkX is heavy. Use FallbackGraph when unavailable.",
         extra_props={"adr_id": "ADR-001"})
    _add("adr2", ["Decision", "ADR"], "ADR-002: Deterministic IDs",
         "Use md5 hash for node IDs to prevent duplicates. See [[ADR-001]].",
         extra_props={"adr_id": "ADR-002"})
    _add("pat1", ["Pattern", "ApprovedPattern"], "PAT-001: Feedback Loop",
         "Run /learn after tasks. Implements [[ADR-001]].",
         extra_props={"pat_id": "PAT-001"})
    _add("pat2", ["Pattern", "ApprovedPattern"], "PAT-002: Dedup Strategy",
         "Merge duplicate nodes by title.",
         extra_props={"pat_id": "PAT-002"})
    _add("commit1", ["Episode", "Commit"], "feat(brain): add fallback graph",
         "Implemented FallbackGraph class.",
         extra_props={"commit_hash": "abc12345", "scope": "brain", "commit_type": "feat",
                      "files": ["brain.py", "tests/test_brain.py"]})
    _add("concept1", ["Concept"], "Engram Memory System",
         "The Engram is a persistent memory system for Claude Code.")
    _add("person1", ["Person"], "Test Developer",
         extra_props={"email": "test@dev.com", "name": "Test Dev", "aliases": ["@testdev"]},
         strength=1.0, access_count=0)

    # Edges
    b.graph.add_edge("adr1", "person1", type="AUTHORED_BY", weight=0.5, props={})
    b.graph.add_edge("adr2", "person1", type="AUTHORED_BY", weight=0.5, props={})
    b.graph.add_edge("pat1", "person1", type="AUTHORED_BY", weight=0.5, props={})
    b.graph.add_edge("pat1", "adr1", type="REFERENCES", weight=0.6, props={})
    b.graph.add_edge("commit1", "person1", type="AUTHORED_BY", weight=0.5, props={})
    b.graph.add_edge("commit1", "pat1", type="APPLIES", weight=0.6, props={})
    b.graph.add_edge("concept1", "person1", type="AUTHORED_BY", weight=0.5, props={})

    return b


# ── Fixture file readers ──


@pytest.fixture
def sample_adr_log():
    """Content of sample_adr_log.md fixture."""
    return (FIXTURES_DIR / "sample_adr_log.md").read_text(encoding="utf-8")


@pytest.fixture
def sample_domain():
    """Content of sample_domain.md fixture."""
    return (FIXTURES_DIR / "sample_domain.md").read_text(encoding="utf-8")


@pytest.fixture
def sample_patterns():
    """Content of sample_patterns.md fixture."""
    return (FIXTURES_DIR / "sample_patterns.md").read_text(encoding="utf-8")


@pytest.fixture
def sample_experiences():
    """Content of sample_experiences.md fixture."""
    return (FIXTURES_DIR / "sample_experiences.md").read_text(encoding="utf-8")
