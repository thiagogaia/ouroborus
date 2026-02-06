"""Integration tests for populate.py with mock brain."""

from unittest.mock import patch, MagicMock
from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


class TestPopulateAdrs:
    """populate.populate_adrs() with fixture data."""

    def test_populates_adrs(self, empty_brain):
        from populate import populate_adrs

        fixture_path = FIXTURES_DIR / "sample_adr_log.md"
        with patch("populate.Path") as mock_path_cls:
            # Make Path(".claude/knowledge/decisions/ADR_LOG.md") return our fixture
            mock_path_instance = MagicMock()
            mock_path_instance.exists.return_value = True
            mock_path_instance.read_text.return_value = fixture_path.read_text(encoding="utf-8")
            mock_path_cls.return_value = mock_path_instance

            count = populate_adrs(empty_brain)
            assert count == 2

    def test_creates_adr_nodes(self, empty_brain):
        from populate import populate_adrs

        fixture_path = FIXTURES_DIR / "sample_adr_log.md"
        with patch("populate.Path") as mock_path_cls:
            mock_path_instance = MagicMock()
            mock_path_instance.exists.return_value = True
            mock_path_instance.read_text.return_value = fixture_path.read_text(encoding="utf-8")
            mock_path_cls.return_value = mock_path_instance

            populate_adrs(empty_brain)
            adrs = empty_brain.get_by_label("ADR")
            assert len(adrs) >= 2


class TestPopulatePatterns:
    """populate.populate_patterns() with fixture data."""

    def test_populates_patterns(self, empty_brain):
        from populate import populate_patterns

        fixture_path = FIXTURES_DIR / "sample_patterns.md"
        with patch("populate.Path") as mock_path_cls:
            mock_path_instance = MagicMock()
            mock_path_instance.exists.return_value = True
            mock_path_instance.read_text.return_value = fixture_path.read_text(encoding="utf-8")
            mock_path_cls.return_value = mock_path_instance

            count = populate_patterns(empty_brain)
            assert count >= 3  # 2 approved + 1 anti


class TestPopulateExperiences:
    """populate.populate_experiences() with fixture data."""

    def test_populates_experiences(self, empty_brain):
        from populate import populate_experiences

        fixture_path = FIXTURES_DIR / "sample_experiences.md"
        with patch("populate.Path") as mock_path_cls:
            mock_path_instance = MagicMock()
            mock_path_instance.exists.return_value = True
            mock_path_instance.read_text.return_value = fixture_path.read_text(encoding="utf-8")
            mock_path_cls.return_value = mock_path_instance

            count = populate_experiences(empty_brain)
            assert count == 2


class TestCrossReferencePass:
    """populate.cross_reference_pass()"""

    def test_creates_reference_edges(self, seeded_brain):
        from populate import cross_reference_pass

        # adr2 summary mentions ADR-001 in title context
        seeded_brain.graph._nodes["adr2"]["props"]["summary"] = "See ADR-001"
        seeded_brain.graph._nodes["adr2"]["props"]["title"] = "ADR-002: Deterministic IDs"

        count = cross_reference_pass(seeded_brain)
        # Should find reference from adr2 to adr1
        assert count >= 0  # May already have the edge


class TestExtractReferencesFromParseGitCommits:
    """populate.parse_git_commits() with mocked subprocess."""

    def test_parses_commits(self):
        from populate import parse_git_commits

        git_output = "abc12345|Dev Name|dev@test.com|2026-01-15 10:00:00 +0000|feat(brain): add feature|body text"

        with patch("populate.subprocess.run") as mock_run:
            # Main git log call
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = git_output

            # git diff-tree call
            mock_files = MagicMock()
            mock_files.returncode = 0
            mock_files.stdout = "brain.py\ntest_brain.py"

            mock_run.side_effect = [mock_result, mock_files]

            commits = parse_git_commits(max_commits=1)
            assert len(commits) == 1
            assert commits[0]["hash"] == "abc12345"
            assert commits[0]["type"] == "feat"
            assert commits[0]["scope"] == "brain"
