"""Tests for parser functions in populate.py."""

import pytest


class TestParseAdrLog:
    """populate.parse_adr_log()"""

    def test_parses_two_adrs(self, sample_adr_log):
        from populate import parse_adr_log
        adrs = parse_adr_log(sample_adr_log)
        assert len(adrs) == 2

    def test_first_adr_id(self, sample_adr_log):
        from populate import parse_adr_log
        adrs = parse_adr_log(sample_adr_log)
        assert adrs[0]["id"] == "ADR-001"

    def test_first_adr_title(self, sample_adr_log):
        from populate import parse_adr_log
        adrs = parse_adr_log(sample_adr_log)
        assert adrs[0]["title"] == "Use FallbackGraph"

    def test_first_adr_date(self, sample_adr_log):
        from populate import parse_adr_log
        adrs = parse_adr_log(sample_adr_log)
        assert adrs[0]["date"] == "2026-01-15"

    def test_first_adr_status(self, sample_adr_log):
        from populate import parse_adr_log
        adrs = parse_adr_log(sample_adr_log)
        assert adrs[0]["status"] == "Aceito"

    def test_first_adr_has_context(self, sample_adr_log):
        from populate import parse_adr_log
        adrs = parse_adr_log(sample_adr_log)
        assert "heavy dependency" in adrs[0]["context"]

    def test_first_adr_has_decision(self, sample_adr_log):
        from populate import parse_adr_log
        adrs = parse_adr_log(sample_adr_log)
        assert "FallbackGraph" in adrs[0]["decision"]

    def test_second_adr_id(self, sample_adr_log):
        from populate import parse_adr_log
        adrs = parse_adr_log(sample_adr_log)
        assert adrs[1]["id"] == "ADR-002"

    def test_second_adr_has_consequences(self, sample_adr_log):
        from populate import parse_adr_log
        adrs = parse_adr_log(sample_adr_log)
        assert "collision" in adrs[1]["consequences"].lower() or "dedup" in adrs[1]["consequences"].lower()

    def test_empty_content_returns_empty(self):
        from populate import parse_adr_log
        assert parse_adr_log("") == []

    def test_no_adr_markers_returns_empty(self):
        from populate import parse_adr_log
        assert parse_adr_log("# Just a header\nSome text.") == []


class TestParseDomain:
    """populate.parse_domain()"""

    def test_extracts_glossary_terms(self, sample_domain):
        from populate import parse_domain
        concepts = parse_domain(sample_domain)
        glossary = [c for c in concepts if c["type"] == "glossary"]
        assert len(glossary) >= 2
        terms = [c["term"] for c in glossary]
        assert "Engram" in terms

    def test_glossary_term_has_definition(self, sample_domain):
        from populate import parse_domain
        concepts = parse_domain(sample_domain)
        engram = next(c for c in concepts if c.get("term") == "Engram")
        assert "memory" in engram["definition"].lower() or "Memory" in engram["definition"]

    def test_extracts_rules(self, sample_domain):
        from populate import parse_domain
        concepts = parse_domain(sample_domain)
        rules = [c for c in concepts if c["type"] == "rule"]
        assert len(rules) >= 1

    def test_rule_has_id_and_description(self, sample_domain):
        from populate import parse_domain
        concepts = parse_domain(sample_domain)
        rules = [c for c in concepts if c["type"] == "rule"]
        assert any("RN-001" in r["id"] for r in rules)

    def test_extracts_entities(self, sample_domain):
        from populate import parse_domain
        concepts = parse_domain(sample_domain)
        entities = [c for c in concepts if c["type"] == "entity"]
        assert len(entities) >= 1
        names = [e["name"] for e in entities]
        assert "Brain" in names

    def test_empty_content(self):
        from populate import parse_domain
        assert parse_domain("") == []


class TestParsePatterns:
    """populate.parse_patterns()"""

    def test_extracts_approved_patterns(self, sample_patterns):
        from populate import parse_patterns
        patterns = parse_patterns(sample_patterns)
        approved = [p for p in patterns if p["type"] == "approved"]
        assert len(approved) >= 2

    def test_approved_pattern_has_name(self, sample_patterns):
        from populate import parse_patterns
        patterns = parse_patterns(sample_patterns)
        approved = [p for p in patterns if p["type"] == "approved"]
        names = [p["name"] for p in approved]
        assert any("PAT-001" in n for n in names)

    def test_extracts_anti_patterns(self, sample_patterns):
        from populate import parse_patterns
        patterns = parse_patterns(sample_patterns)
        anti = [p for p in patterns if p["type"] == "anti"]
        assert len(anti) >= 1

    def test_anti_pattern_has_description(self, sample_patterns):
        from populate import parse_patterns
        patterns = parse_patterns(sample_patterns)
        anti = [p for p in patterns if p["type"] == "anti"]
        assert any("uuid" in p["description"].lower() or "UUID" in p["name"] for p in anti)

    def test_empty_content(self):
        from populate import parse_patterns
        assert parse_patterns("") == []


class TestExtractReferences:
    """populate._extract_references()"""

    def test_extracts_adr_reference(self):
        from populate import _extract_references
        refs = _extract_references("See ADR-001 for details")
        assert "ADR-001" in refs

    def test_extracts_pat_reference(self):
        from populate import _extract_references
        refs = _extract_references("Follows PAT-12 convention")
        assert "PAT-012" in refs

    def test_extracts_exp_reference(self):
        from populate import _extract_references
        refs = _extract_references("Based on EXP-3")
        assert "EXP-003" in refs

    def test_extracts_wikilink(self):
        from populate import _extract_references
        refs = _extract_references("See [[FallbackGraph]] for impl")
        assert "FallbackGraph" in refs

    def test_deduplicates(self):
        from populate import _extract_references
        refs = _extract_references("ADR-001 and ADR-001 again")
        assert refs.count("ADR-001") == 1

    def test_mixed_references(self):
        from populate import _extract_references
        refs = _extract_references("ADR-001, PAT-002, [[concept]]")
        assert "ADR-001" in refs
        assert "PAT-002" in refs
        assert "concept" in refs

    def test_empty_content(self):
        from populate import _extract_references
        assert _extract_references("") == []

    def test_no_references(self):
        from populate import _extract_references
        assert _extract_references("Just plain text without references") == []

    def test_case_insensitive_adr(self):
        from populate import _extract_references
        refs = _extract_references("see adr-5 here")
        assert "ADR-005" in refs
