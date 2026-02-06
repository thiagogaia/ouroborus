"""Tests for Brain save/load roundtrip."""

import json

import pytest


class TestPersistence:
    """Brain.save() and Brain.load() roundtrip."""

    def test_save_creates_graph_json(self, seeded_brain):
        seeded_brain.save()
        graph_file = seeded_brain.base_path / "graph.json"
        assert graph_file.exists()

    def test_save_valid_json(self, seeded_brain):
        seeded_brain.save()
        graph_file = seeded_brain.base_path / "graph.json"
        data = json.loads(graph_file.read_text(encoding="utf-8"))
        assert "version" in data
        assert "nodes" in data
        assert "edges" in data

    def test_roundtrip_preserves_nodes(self, seeded_brain):
        from brain import Brain

        seeded_brain.save()
        loaded = Brain(base_path=seeded_brain.base_path)
        loaded.load()

        assert loaded.graph.number_of_nodes() == seeded_brain.graph.number_of_nodes()

    def test_roundtrip_preserves_edges(self, seeded_brain):
        from brain import Brain

        seeded_brain.save()
        loaded = Brain(base_path=seeded_brain.base_path)
        loaded.load()

        assert loaded.graph.number_of_edges() == seeded_brain.graph.number_of_edges()

    def test_roundtrip_preserves_node_data(self, seeded_brain):
        from brain import Brain

        seeded_brain.save()
        loaded = Brain(base_path=seeded_brain.base_path)
        loaded.load()

        original = seeded_brain.get_node("adr1")
        restored = loaded.get_node("adr1")
        assert restored is not None
        assert restored["props"]["title"] == original["props"]["title"]
        assert restored["labels"] == original["labels"]

    def test_load_nonexistent_returns_false(self, tmp_path):
        from brain import Brain

        b = Brain(base_path=tmp_path / "nonexistent")
        assert b.load() is False

    def test_load_empty_brain_then_save(self, empty_brain):
        empty_brain.save()
        graph_file = empty_brain.base_path / "graph.json"
        assert graph_file.exists()
        data = json.loads(graph_file.read_text())
        assert data["nodes"] == {}
        assert data["edges"] == []
