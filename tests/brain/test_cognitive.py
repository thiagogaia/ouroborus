"""Tests for cognitive.py functions."""

import json
from datetime import datetime

import pytest


class TestHealthCheck:
    """cognitive.health_check()"""

    def test_returns_health_score(self, seeded_brain):
        from cognitive import health_check
        result = health_check(seeded_brain)
        assert "health_score" in result
        assert 0.0 <= result["health_score"] <= 1.0

    def test_returns_status(self, seeded_brain):
        from cognitive import health_check
        result = health_check(seeded_brain)
        assert result["status"] in ("healthy", "needs_attention", "critical")

    def test_returns_recommendations(self, seeded_brain):
        from cognitive import health_check
        result = health_check(seeded_brain)
        assert "recommendations" in result
        assert isinstance(result["recommendations"], list)
        assert len(result["recommendations"]) > 0

    def test_empty_brain_is_healthy(self, empty_brain):
        from cognitive import health_check
        result = health_check(empty_brain)
        # Empty brain: score = 1.0 (special case)
        assert result["health_score"] == 1.0
        assert result["status"] == "healthy"

    def test_includes_node_stats(self, seeded_brain):
        from cognitive import health_check
        result = health_check(seeded_brain)
        assert "nodes" in result
        assert "edges" in result
        assert result["nodes"] == 7


class TestGetRecommendations:
    """cognitive.get_recommendations()"""

    def test_ok_when_healthy(self):
        from cognitive import get_recommendations
        stats = {
            "nodes": 100,
            "weak_memories": 5,
            "embeddings": 80,
            "semantic_edges": 80,
            "avg_degree": 3.0,
        }
        recs = get_recommendations(stats, 0.9)
        assert len(recs) == 1
        assert recs[0]["type"] == "ok"

    def test_recommends_archive_for_many_weak(self):
        from cognitive import get_recommendations
        stats = {
            "nodes": 100,
            "weak_memories": 50,  # 50% weak
            "embeddings": 80,
            "semantic_edges": 80,
            "avg_degree": 3.0,
        }
        recs = get_recommendations(stats, 0.5)
        types = [r["type"] for r in recs]
        assert "archive" in types

    def test_recommends_embeddings_when_low(self):
        from cognitive import get_recommendations
        stats = {
            "nodes": 100,
            "weak_memories": 5,
            "embeddings": 10,  # only 10%
            "semantic_edges": 80,
            "avg_degree": 3.0,
        }
        recs = get_recommendations(stats, 0.5)
        types = [r["type"] for r in recs]
        assert "embeddings" in types

    def test_recommends_sleep_when_few_semantic_edges(self):
        from cognitive import get_recommendations
        stats = {
            "nodes": 100,
            "weak_memories": 5,
            "embeddings": 80,
            "semantic_edges": 10,  # only 10%
            "avg_degree": 3.0,
        }
        recs = get_recommendations(stats, 0.5)
        types = [r["type"] for r in recs]
        assert "sleep" in types

    def test_recommends_connections_for_low_degree(self):
        from cognitive import get_recommendations
        stats = {
            "nodes": 100,
            "weak_memories": 5,
            "embeddings": 80,
            "semantic_edges": 80,
            "avg_degree": 1.0,  # low connectivity
        }
        recs = get_recommendations(stats, 0.5)
        types = [r["type"] for r in recs]
        assert "connections" in types


class TestArchive:
    """cognitive.archive()"""

    def test_archives_weak_nodes(self, seeded_brain):
        from cognitive import archive

        # Make concept1 very weak
        seeded_brain.graph._nodes["concept1"]["memory"]["strength"] = 0.05
        result = archive(seeded_brain)
        assert result["archived_count"] >= 1
        assert "concept1" in result["archived_nodes"]

    def test_does_not_archive_protected(self, seeded_brain):
        from cognitive import archive

        # Make person weak but it should be protected
        seeded_brain.graph._nodes["person1"]["memory"]["strength"] = 0.01
        # Make decision weak but it should be protected
        seeded_brain.graph._nodes["adr1"]["memory"]["strength"] = 0.01
        result = archive(seeded_brain)
        assert "person1" not in result["archived_nodes"]
        assert "adr1" not in result["archived_nodes"]

    def test_skips_already_archived(self, seeded_brain):
        from cognitive import archive

        seeded_brain.graph._nodes["concept1"]["memory"]["strength"] = 0.01
        seeded_brain.graph._nodes["concept1"]["labels"].append("Archived")
        result = archive(seeded_brain)
        assert "concept1" not in result["archived_nodes"]

    def test_archive_returns_metadata(self, seeded_brain):
        from cognitive import archive
        result = archive(seeded_brain)
        assert "ran_at" in result
        assert result["type"] == "archive"


class TestLogJob:
    """cognitive.log_job()"""

    def test_creates_log_file(self, tmp_path):
        from cognitive import log_job
        log_path = tmp_path / "log.jsonl"
        log_job({"type": "test", "count": 42}, log_path=log_path)
        assert log_path.exists()

    def test_appends_json_line(self, tmp_path):
        from cognitive import log_job
        log_path = tmp_path / "log.jsonl"
        log_job({"type": "first"}, log_path=log_path)
        log_job({"type": "second"}, log_path=log_path)

        lines = log_path.read_text().strip().split("\n")
        assert len(lines) == 2
        assert json.loads(lines[0])["type"] == "first"
        assert json.loads(lines[1])["type"] == "second"
