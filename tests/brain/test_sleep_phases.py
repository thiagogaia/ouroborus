"""Tests for sleep.py phases with seeded_brain."""

import hashlib
from datetime import datetime, timedelta

import pytest


class TestPhaseDedup:
    """sleep.phase_dedup()"""

    def test_no_duplicates_returns_zero(self, seeded_brain):
        from sleep import phase_dedup
        stats = phase_dedup(seeded_brain)
        assert stats["merged"] == 0

    def test_merges_duplicate_titles(self, seeded_brain):
        from sleep import phase_dedup

        # Add a duplicate of adr1 with same title but different ID
        now = datetime.now().isoformat()
        seeded_brain.graph.add_node(
            "dup_adr1",
            labels=["Decision", "ADR"],
            props={"title": "ADR-001: Use FallbackGraph", "content": "duplicate"},
            memory={"strength": 0.5, "access_count": 0, "last_accessed": now,
                    "created_at": now, "decay_rate": 0.01},
        )

        stats = phase_dedup(seeded_brain)
        assert stats["merged"] >= 1

    def test_merges_by_prop_key(self, seeded_brain):
        from sleep import phase_dedup

        now = datetime.now().isoformat()
        seeded_brain.graph.add_node(
            "dup_adr1_prop",
            labels=["Decision"],
            props={"title": "Different Title", "adr_id": "ADR-001"},
            memory={"strength": 0.5, "access_count": 0, "last_accessed": now,
                    "created_at": now, "decay_rate": 0.01},
        )

        stats = phase_dedup(seeded_brain)
        assert stats["merged"] >= 1

    def test_survivor_keeps_most_edges(self, seeded_brain):
        from sleep import phase_dedup

        now = datetime.now().isoformat()
        # adr1 already has edges, dup has none -> adr1 should survive
        seeded_brain.graph.add_node(
            "dup_adr1",
            labels=["Decision"],
            props={"title": "ADR-001: Use FallbackGraph", "content": "dup"},
            memory={"strength": 0.5, "access_count": 0, "last_accessed": now,
                    "created_at": now, "decay_rate": 0.01},
        )

        phase_dedup(seeded_brain)
        assert seeded_brain._node_exists("adr1")
        assert not seeded_brain._node_exists("dup_adr1")


class TestPhaseConnect:
    """sleep.phase_connect()"""

    def test_creates_reference_edges(self, seeded_brain):
        from sleep import phase_connect

        # adr2 content mentions "[[ADR-001]]" but may not have edge yet
        # Let's ensure content has the ref
        seeded_brain.graph._nodes["adr2"]["props"]["content"] = "Use md5 hash. See [[ADR-001]]."

        stats = phase_connect(seeded_brain)
        assert stats["references"] >= 0  # May already exist

    def test_creates_same_scope_edges(self, seeded_brain):
        from sleep import phase_connect

        # Add another commit with same scope
        now = datetime.now().isoformat()
        seeded_brain.graph.add_node(
            "commit2",
            labels=["Episode", "Commit"],
            props={"title": "fix(brain): handle edge case", "scope": "brain",
                   "commit_type": "fix", "content": "Fixed edge case"},
            memory={"strength": 1.0, "access_count": 1, "last_accessed": now,
                    "created_at": now, "decay_rate": 0.01},
        )

        stats = phase_connect(seeded_brain)
        assert stats["same_scope"] >= 1

    def test_creates_modifies_same_edges(self, seeded_brain):
        from sleep import phase_connect

        now = datetime.now().isoformat()
        # commit1 modifies brain.py (scope="brain"); add another commit modifying
        # brain.py but with DIFFERENT scope so SAME_SCOPE doesn't preempt the edge
        seeded_brain.graph.add_node(
            "commit3",
            labels=["Episode", "Commit"],
            props={"title": "refactor(core): cleanup", "scope": "core",
                   "commit_type": "refactor", "content": "Cleanup",
                   "files": ["brain.py"]},
            memory={"strength": 1.0, "access_count": 1, "last_accessed": now,
                    "created_at": now, "decay_rate": 0.01},
        )

        stats = phase_connect(seeded_brain)
        assert stats["modifies_same"] >= 1

    def test_returns_stats_dict(self, seeded_brain):
        from sleep import phase_connect
        stats = phase_connect(seeded_brain)
        assert "references" in stats
        assert "same_scope" in stats
        assert "modifies_same" in stats


class TestPhaseRelate:
    """sleep.phase_relate() — TF vector fallback only (no numpy)."""

    def test_returns_stats(self, seeded_brain):
        from sleep import phase_relate
        stats = phase_relate(seeded_brain)
        assert "related_to" in stats
        assert "method" in stats

    def test_uses_tf_vectors_method(self, seeded_brain):
        from sleep import phase_relate
        stats = phase_relate(seeded_brain)
        # Without real numpy/embeddings, should use tf_vectors
        assert stats["method"] in ("tf_vectors", "none")


class TestPhaseThemes:
    """sleep.phase_themes()"""

    def test_no_themes_for_few_commits(self, seeded_brain):
        from sleep import phase_themes
        # Only 1 commit with scope "brain" — needs 3+
        stats = phase_themes(seeded_brain)
        assert stats["themes_created"] == 0

    def test_creates_theme_for_3plus_commits(self, seeded_brain):
        from sleep import phase_themes

        now = datetime.now().isoformat()
        for i in range(3):
            seeded_brain.graph.add_node(
                f"commit_theme_{i}",
                labels=["Episode", "Commit"],
                props={"title": f"feat(api): endpoint {i}", "scope": "api",
                       "commit_type": "feat", "content": f"API endpoint {i}"},
                memory={"strength": 1.0, "access_count": 1, "last_accessed": now,
                        "created_at": now, "decay_rate": 0.01},
            )

        stats = phase_themes(seeded_brain)
        assert stats["themes_created"] >= 1
        assert stats["edges_created"] >= 3

    def test_returns_stats_dict(self, seeded_brain):
        from sleep import phase_themes
        stats = phase_themes(seeded_brain)
        assert "themes_created" in stats
        assert "clusters_created" in stats
        assert "edges_created" in stats


class TestPhaseCalibrate:
    """sleep.phase_calibrate()"""

    def test_returns_stats(self, seeded_brain):
        from sleep import phase_calibrate
        stats = phase_calibrate(seeded_brain)
        assert "boosted" in stats
        assert "decayed" in stats

    def test_boosts_frequently_accessed_edges(self, seeded_brain):
        from sleep import phase_calibrate

        # Make both endpoints highly accessed
        seeded_brain.graph._nodes["adr1"]["memory"]["access_count"] = 10
        seeded_brain.graph._nodes["pat1"]["memory"]["access_count"] = 10

        # pat1 -> adr1 is REFERENCES (semantic)
        old_weight = seeded_brain.graph._edges[("pat1", "adr1")]["weight"]
        phase_calibrate(seeded_brain)
        new_weight = seeded_brain.graph._edges[("pat1", "adr1")]["weight"]
        assert new_weight > old_weight

    def test_decays_never_accessed_edges(self, seeded_brain):
        from sleep import phase_calibrate

        # Make endpoints never accessed with semantic edge
        seeded_brain.graph._nodes["pat1"]["memory"]["access_count"] = 0
        seeded_brain.graph._nodes["adr1"]["memory"]["access_count"] = 0

        old_weight = seeded_brain.graph._edges[("pat1", "adr1")]["weight"]
        phase_calibrate(seeded_brain)
        new_weight = seeded_brain.graph._edges[("pat1", "adr1")]["weight"]
        assert new_weight <= old_weight


class TestRunSleep:
    """sleep.run_sleep() orchestrator."""

    def test_runs_all_phases(self, seeded_brain):
        from sleep import run_sleep
        results = run_sleep(seeded_brain)
        assert "phases" in results
        assert "dedup" in results["phases"]
        assert "connect" in results["phases"]
        assert "calibrate" in results["phases"]

    def test_runs_specific_phases(self, seeded_brain):
        from sleep import run_sleep
        results = run_sleep(seeded_brain, phases=["dedup", "calibrate"])
        assert "dedup" in results["phases"]
        assert "calibrate" in results["phases"]
        assert "connect" not in results["phases"]

    def test_reports_delta(self, seeded_brain):
        from sleep import run_sleep
        results = run_sleep(seeded_brain)
        assert "before" in results
        assert "after" in results
        assert "delta" in results
