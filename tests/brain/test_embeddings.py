"""Tests for embeddings.py with fully mocked dependencies."""

import json
from unittest.mock import patch, MagicMock
from pathlib import Path

import pytest


class TestBuildEmbeddings:
    """embeddings.build_embeddings() — fully mocked."""

    def test_build_creates_npz(self, tmp_path):
        # Create a brain.db with one node via BrainSQLite
        from brain_sqlite import BrainSQLite
        brain = BrainSQLite(base_path=tmp_path)
        brain.load()
        brain.add_node_raw(
            "n1",
            labels=["Concept"],
            props={"title": "Test Node", "content": "Some content", "summary": "short"},
            memory={"strength": 1.0},
        )

        # Mock get_embedding to return a fake vector
        fake_vector = [0.1, 0.2, 0.3]

        # We need to mock numpy's savez_compressed since it's called
        import sys
        np_mock = sys.modules["numpy"]

        with patch("embeddings.get_embedding", return_value=fake_vector):
            with patch.object(np_mock, "savez_compressed") as mock_save:
                from embeddings import build_embeddings
                build_embeddings(brain_path=tmp_path)
                mock_save.assert_called_once()


class TestSearchEmbeddings:
    """embeddings.search_embeddings() — fully mocked."""

    def test_search_returns_results(self, tmp_path):
        import sys
        np_mock = sys.modules["numpy"]

        # Create a brain.db with one node via BrainSQLite
        from brain_sqlite import BrainSQLite
        brain = BrainSQLite(base_path=tmp_path)
        brain.load()
        brain.add_node_raw(
            "n1",
            labels=["Concept"],
            props={"title": "Auth System", "summary": "Authentication"},
            memory={"strength": 1.0},
        )

        # Create fake embeddings.npz
        fake_npz = MagicMock()
        fake_npz.files = ["n1"]
        fake_npz.__getitem__ = lambda self, k: [0.1, 0.2, 0.3]

        with patch("embeddings.get_embedding", return_value=[0.1, 0.2, 0.3]), \
             patch.object(np_mock, "load", return_value=fake_npz):
            # Make npz file exist
            (tmp_path / "embeddings.npz").write_text("fake")

            from embeddings import search_embeddings
            results = search_embeddings("auth", brain_path=tmp_path, top_k=5)
            assert len(results) >= 1
            assert results[0]["id"] == "n1"
