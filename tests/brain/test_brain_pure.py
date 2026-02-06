"""Tests for pure functions in brain.py (no side effects)."""

import hashlib
from unittest.mock import patch, MagicMock

import pytest


class TestGenerateSummary:
    """brain._generate_summary()"""

    def test_short_text_returned_as_is(self):
        from brain import Brain
        b = Brain.__new__(Brain)
        assert b._generate_summary("Hello world") == "Hello world"

    def test_strips_markdown_headers(self):
        from brain import Brain
        b = Brain.__new__(Brain)
        result = b._generate_summary("## Header\nSome text")
        assert "##" not in result
        assert "Header" in result

    def test_strips_bold_markers(self):
        from brain import Brain
        b = Brain.__new__(Brain)
        result = b._generate_summary("Use **bold** text")
        assert "**" not in result
        assert "bold" in result

    def test_strips_wikilinks(self):
        from brain import Brain
        b = Brain.__new__(Brain)
        result = b._generate_summary("See [[ADR-001]] for details")
        assert "[[" not in result
        assert "ADR-001" in result

    def test_collapses_newlines(self):
        from brain import Brain
        b = Brain.__new__(Brain)
        result = b._generate_summary("Line 1\n\nLine 2\n\nLine 3")
        assert "\n" not in result
        assert "Line 1" in result

    def test_truncates_long_text(self):
        from brain import Brain
        b = Brain.__new__(Brain)
        long_text = "A" * 600
        result = b._generate_summary(long_text, max_length=100)
        assert len(result) == 100
        assert result.endswith("...")

    def test_exact_max_length_not_truncated(self):
        from brain import Brain
        b = Brain.__new__(Brain)
        text = "X" * 500
        result = b._generate_summary(text, max_length=500)
        assert result == text
        assert "..." not in result


class TestGetDecayRate:
    """brain._get_decay_rate()"""

    def test_decision_slowest_decay(self):
        from brain import Brain
        b = Brain.__new__(Brain)
        assert b._get_decay_rate(["Decision"]) == 0.001

    def test_pattern_decay(self):
        from brain import Brain
        b = Brain.__new__(Brain)
        assert b._get_decay_rate(["Pattern"]) == 0.005

    def test_concept_decay(self):
        from brain import Brain
        b = Brain.__new__(Brain)
        assert b._get_decay_rate(["Concept"]) == 0.003

    def test_episode_decay(self):
        from brain import Brain
        b = Brain.__new__(Brain)
        assert b._get_decay_rate(["Episode"]) == 0.01

    def test_person_near_zero_decay(self):
        from brain import Brain
        b = Brain.__new__(Brain)
        assert b._get_decay_rate(["Person"]) == 0.0001

    def test_unknown_label_default(self):
        from brain import Brain
        b = Brain.__new__(Brain)
        assert b._get_decay_rate(["SomethingNew"]) == 0.02

    def test_first_match_wins(self):
        from brain import Brain
        b = Brain.__new__(Brain)
        # Decision comes first in the if/elif chain
        assert b._get_decay_rate(["Decision", "Episode"]) == 0.001


class TestInferDomain:
    """brain._infer_domain()"""

    def test_auth_keywords(self):
        from brain import Brain
        b = Brain.__new__(Brain)
        assert b._infer_domain("JWT token authentication login", []) == "auth"

    def test_database_keywords(self):
        from brain import Brain
        b = Brain.__new__(Brain)
        assert b._infer_domain("PostgreSQL database migration query", []) == "database"

    def test_no_domain_for_generic_text(self):
        from brain import Brain
        b = Brain.__new__(Brain)
        assert b._infer_domain("this is generic text", []) is None

    def test_highest_score_wins(self):
        from brain import Brain
        b = Brain.__new__(Brain)
        # "test mock fixture coverage" has 4 testing keywords
        result = b._infer_domain("test mock fixture coverage", [])
        assert result == "testing"

    def test_case_insensitive(self):
        from brain import Brain
        b = Brain.__new__(Brain)
        assert b._infer_domain("DOCKER Deploy AWS Cloud", []) == "infra"


class TestExtractLinks:
    """brain._extract_links()"""

    def test_simple_wikilink(self):
        from brain import Brain
        b = Brain.__new__(Brain)
        assert b._extract_links("See [[ADR-001]] for details") == ["ADR-001"]

    def test_multiple_wikilinks(self):
        from brain import Brain
        b = Brain.__new__(Brain)
        result = b._extract_links("Use [[ADR-001]] and [[PAT-002]]")
        assert "ADR-001" in result
        assert "PAT-002" in result

    def test_wikilink_with_display_text(self):
        from brain import Brain
        b = Brain.__new__(Brain)
        result = b._extract_links("See [[ADR-001|the decision]]")
        assert result == ["ADR-001"]

    def test_no_wikilinks(self):
        from brain import Brain
        b = Brain.__new__(Brain)
        assert b._extract_links("No links here") == []

    def test_empty_string(self):
        from brain import Brain
        b = Brain.__new__(Brain)
        assert b._extract_links("") == []


class TestGetCurrentDeveloper:
    """brain.get_current_developer()"""

    def test_returns_git_email_and_name(self):
        from brain import get_current_developer

        with patch("brain.subprocess.check_output") as mock_co:
            mock_co.side_effect = [
                "dev@example.com\n",  # git config user.email
                "Dev Name\n",         # git config user.name
            ]
            result = get_current_developer()
            assert result["email"] == "dev@example.com"
            assert result["name"] == "Dev Name"
            assert result["author"] == "dev@example.com"

    def test_fallback_on_git_failure(self):
        from brain import get_current_developer

        with patch("brain.subprocess.check_output", side_effect=Exception("no git")):
            with patch("getpass.getuser", return_value="testuser"):
                result = get_current_developer()
                assert result["email"] == "testuser@local"
                assert result["name"] == "testuser"
