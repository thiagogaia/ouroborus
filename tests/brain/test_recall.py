"""Tests for recall.py functions."""

from unittest.mock import patch, MagicMock

import pytest


class TestFormatHumanReadable:
    """recall.format_human_readable()"""

    def test_formats_error(self):
        from recall import format_human_readable
        data = {"error": "Something broke", "fallback": "Try this"}
        result = format_human_readable(data)
        assert "Something broke" in result
        assert "Try this" in result

    def test_formats_empty_results(self):
        from recall import format_human_readable
        data = {"query": "test", "total": 0, "results": []}
        result = format_human_readable(data)
        assert "Nenhuma" in result
        assert "test" in result

    def test_formats_results_with_connections(self):
        from recall import format_human_readable
        data = {
            "query": "auth",
            "total": 1,
            "results": [
                {
                    "id": "n1",
                    "title": "Auth Pattern",
                    "type": "Pattern",
                    "labels": ["Pattern"],
                    "summary": "Authentication pattern",
                    "content": "Full content here",
                    "score": 0.8,
                    "author": "dev@test.com",
                    "connections": [
                        {"target": "n2", "title": "Related ADR", "type": "REFERENCES", "weight": 0.6}
                    ],
                }
            ],
        }
        result = format_human_readable(data)
        assert "Auth Pattern" in result
        assert "dev@test.com" in result
        assert "REFERENCES" in result
        assert "Related ADR" in result

    def test_score_bar_rendering(self):
        from recall import format_human_readable
        data = {
            "query": "test",
            "total": 1,
            "results": [
                {
                    "id": "n1",
                    "title": "Test",
                    "type": "Concept",
                    "labels": ["Concept"],
                    "summary": "A test",
                    "content": None,
                    "score": 1.0,
                    "author": None,
                    "connections": [],
                }
            ],
        }
        result = format_human_readable(data)
        assert "█" in result


class TestSearchBrain:
    """recall.search_brain() — needs mocked Brain."""

    def test_returns_error_when_deps_missing(self):
        from recall import search_brain

        with patch("recall.HAS_DEPS", False):
            # IMPORT_ERROR may not exist when HAS_DEPS is True, so create it
            with patch("recall.IMPORT_ERROR", "test error", create=True):
                result = search_brain("test query")
                assert "error" in result

    def test_text_search_returns_results(self, seeded_brain):
        """Integration test: search_brain with a real seeded brain."""
        from recall import search_brain

        # Mock Brain() and brain.load() to return our seeded_brain
        mock_brain_cls = MagicMock(return_value=seeded_brain)
        seeded_brain.load = MagicMock(return_value=True)
        seeded_brain.save = MagicMock()

        with patch("recall.HAS_DEPS", True), \
             patch("recall.Brain", mock_brain_cls), \
             patch("recall.HAS_EMBEDDINGS", False):
            result = search_brain("FallbackGraph", top_k=5)
            assert result["total"] > 0
            assert result["results"][0]["title"]
