"""Tests for FallbackGraph standalone functionality."""

import sys
from pathlib import Path

import pytest


class TestFallbackGraphBasic:
    """Basic node and edge operations."""

    def test_add_node_creates_entry(self):
        from brain import FallbackGraph

        g = FallbackGraph()
        g.add_node("n1", label="test")
        assert "n1" in g._nodes
        assert g._nodes["n1"]["label"] == "test"

    def test_add_node_initializes_adjacency(self):
        from brain import FallbackGraph

        g = FallbackGraph()
        g.add_node("n1")
        assert "n1" in g._adj_out
        assert "n1" in g._adj_in
        assert g._adj_out["n1"] == []
        assert g._adj_in["n1"] == []

    def test_add_node_with_multiple_attrs(self):
        from brain import FallbackGraph

        g = FallbackGraph()
        g.add_node("n1", labels=["A", "B"], props={"x": 1})
        assert g._nodes["n1"]["labels"] == ["A", "B"]
        assert g._nodes["n1"]["props"] == {"x": 1}

    def test_add_edge_creates_entry(self):
        from brain import FallbackGraph

        g = FallbackGraph()
        g.add_node("a")
        g.add_node("b")
        g.add_edge("a", "b", type="REF", weight=0.5)
        assert ("a", "b") in g._edges
        assert g._edges[("a", "b")]["type"] == "REF"
        assert g._edges[("a", "b")]["weight"] == 0.5

    def test_add_edge_updates_adjacency(self):
        from brain import FallbackGraph

        g = FallbackGraph()
        g.add_node("a")
        g.add_node("b")
        g.add_edge("a", "b")
        assert "b" in g._adj_out["a"]
        assert "a" in g._adj_in["b"]

    def test_add_edge_no_duplicate_adjacency(self):
        from brain import FallbackGraph

        g = FallbackGraph()
        g.add_node("a")
        g.add_node("b")
        g.add_edge("a", "b")
        g.add_edge("a", "b")  # second time
        assert g._adj_out["a"].count("b") == 1
        assert g._adj_in["b"].count("a") == 1

    def test_add_edge_creates_adjacency_for_missing_nodes(self):
        from brain import FallbackGraph

        g = FallbackGraph()
        g.add_edge("x", "y", type="T")
        assert "y" in g._adj_out.get("x", [])
        assert "x" in g._adj_in.get("y", [])


class TestFallbackGraphTraversal:
    """Successors, predecessors, degree."""

    def test_successors_returns_out_neighbors(self):
        from brain import FallbackGraph

        g = FallbackGraph()
        g.add_node("a")
        g.add_node("b")
        g.add_node("c")
        g.add_edge("a", "b")
        g.add_edge("a", "c")
        assert set(g.successors("a")) == {"b", "c"}

    def test_successors_empty_for_leaf(self):
        from brain import FallbackGraph

        g = FallbackGraph()
        g.add_node("a")
        assert g.successors("a") == []

    def test_successors_empty_for_unknown_node(self):
        from brain import FallbackGraph

        g = FallbackGraph()
        assert g.successors("missing") == []

    def test_predecessors_returns_in_neighbors(self):
        from brain import FallbackGraph

        g = FallbackGraph()
        g.add_node("a")
        g.add_node("b")
        g.add_edge("a", "b")
        g.add_edge("a", "b")  # no dup
        assert g.predecessors("b") == ["a"]

    def test_predecessors_empty_for_root(self):
        from brain import FallbackGraph

        g = FallbackGraph()
        g.add_node("root")
        g.add_node("child")
        g.add_edge("root", "child")
        assert g.predecessors("root") == []

    def test_degree_returns_total_degree(self):
        from brain import FallbackGraph

        g = FallbackGraph()
        g.add_node("a")
        g.add_node("b")
        g.add_node("c")
        g.add_edge("a", "b")
        g.add_edge("c", "a")
        # a: out=1 (->b) + in=1 (<-c) = 2
        degrees = dict(g.degree())
        assert degrees["a"] == 2
        assert degrees["b"] == 1  # in=1
        assert degrees["c"] == 1  # out=1


class TestFallbackGraphProperties:
    """nodes, edges, number_of_*."""

    def test_nodes_property(self):
        from brain import FallbackGraph

        g = FallbackGraph()
        g.add_node("n1", x=1)
        g.add_node("n2", x=2)
        assert g.nodes == {"n1": {"x": 1}, "n2": {"x": 2}}

    def test_edges_property(self):
        from brain import FallbackGraph

        g = FallbackGraph()
        g.add_edge("a", "b", t="X")
        assert g.edges == {("a", "b"): {"t": "X"}}

    def test_number_of_nodes(self):
        from brain import FallbackGraph

        g = FallbackGraph()
        assert g.number_of_nodes() == 0
        g.add_node("a")
        g.add_node("b")
        assert g.number_of_nodes() == 2

    def test_number_of_edges(self):
        from brain import FallbackGraph

        g = FallbackGraph()
        assert g.number_of_edges() == 0
        g.add_edge("a", "b")
        assert g.number_of_edges() == 1
