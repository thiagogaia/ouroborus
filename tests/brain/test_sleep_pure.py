"""Tests for pure functions in sleep.py."""

import pytest


class TestExtractAllRefs:
    """sleep._extract_all_refs()"""

    def test_extracts_adr_refs(self):
        from sleep import _extract_all_refs
        refs = _extract_all_refs("Follows ADR-001 and ADR-002")
        assert "ADR-001" in refs
        assert "ADR-002" in refs

    def test_extracts_pat_refs(self):
        from sleep import _extract_all_refs
        refs = _extract_all_refs("Uses PAT-5")
        assert "PAT-005" in refs

    def test_extracts_exp_refs(self):
        from sleep import _extract_all_refs
        refs = _extract_all_refs("Based on EXP-10")
        assert "EXP-010" in refs

    def test_extracts_wikilinks(self):
        from sleep import _extract_all_refs
        refs = _extract_all_refs("See [[FallbackGraph]] and [[Brain]]")
        assert "FallbackGraph" in refs
        assert "Brain" in refs

    def test_wikilink_with_display(self):
        from sleep import _extract_all_refs
        refs = _extract_all_refs("See [[ADR-001|the decision]]")
        assert "ADR-001" in refs

    def test_deduplicates(self):
        from sleep import _extract_all_refs
        refs = _extract_all_refs("ADR-001 and ADR-001 again")
        assert refs.count("ADR-001") == 1

    def test_empty_text(self):
        from sleep import _extract_all_refs
        assert _extract_all_refs("") == []

    def test_case_insensitive(self):
        from sleep import _extract_all_refs
        refs = _extract_all_refs("See adr-3")
        assert "ADR-003" in refs


class TestTextToVector:
    """sleep._text_to_vector()"""

    def test_returns_none_without_vocab(self):
        from sleep import _text_to_vector
        assert _text_to_vector("some text") is None

    def test_returns_none_for_empty_text(self):
        from sleep import _text_to_vector
        assert _text_to_vector("", vocab={"test": 0}) is None

    def test_returns_none_for_whitespace(self):
        from sleep import _text_to_vector
        assert _text_to_vector("   ", vocab={"test": 0}) is None

    def test_returns_none_for_short_words_only(self):
        from sleep import _text_to_vector
        # Words < 3 chars are filtered out
        assert _text_to_vector("a an to", vocab={"test": 0}) is None

    def test_creates_vector_with_vocab(self):
        from sleep import _text_to_vector
        vocab = {"hello": 0, "world": 1, "test": 2}
        vec = _text_to_vector("Hello world", vocab)
        assert vec is not None
        assert len(vec) == 3
        assert vec[0] > 0  # "hello" present
        assert vec[1] > 0  # "world" present
        assert vec[2] == 0  # "test" absent

    def test_vector_is_normalized(self):
        from sleep import _text_to_vector
        vocab = {"hello": 0, "world": 1}
        vec = _text_to_vector("hello world", vocab)
        norm = sum(v * v for v in vec) ** 0.5
        assert abs(norm - 1.0) < 1e-6

    def test_repeated_word_increases_weight(self):
        from sleep import _text_to_vector
        vocab = {"hello": 0, "world": 1}
        vec = _text_to_vector("hello hello hello world", vocab)
        # "hello" appears 3x, "world" 1x — after normalize hello should be larger
        assert vec[0] > vec[1]


class TestReadNodeContent:
    """sleep._read_node_content()"""

    def test_returns_content_from_props(self):
        from sleep import _read_node_content
        # brain param not used for in-graph content
        result = _read_node_content(None, {"content": "full text", "summary": "short"})
        assert result == "full text"

    def test_falls_back_to_summary(self):
        from sleep import _read_node_content
        result = _read_node_content(None, {"summary": "short text"})
        assert result == "short text"

    def test_returns_empty_for_no_content(self):
        from sleep import _read_node_content
        result = _read_node_content(None, {})
        assert result == ""
