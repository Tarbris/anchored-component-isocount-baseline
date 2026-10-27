import copy
import json
from pathlib import Path
import subprocess
import sys
import unittest

from graph_catalog import Graph, check_mapping, inspect_graph


def graph(directed=False):
    return {"directed": directed,
            "nodes": [{"id": "a", "label": "node"}, {"id": "b", "label": "node"}],
            "edges": [["a", "b", "edge"], ["a", "a", "loop"]]}


class BaselineTests(unittest.TestCase):
    def test_summary_and_purity(self):
        value = graph()
        before = copy.deepcopy(value)
        self.assertEqual(inspect_graph(value), {"directed": False, "nodes": 2, "edges": 2,
                         "self_loops": 1, "node_labels": [{"label": "node", "count": 2}]})
        self.assertEqual(value, before)

    def test_undirected_orientation(self):
        left, right = graph(), graph()
        right["edges"][0][:2] = ["b", "a"]
        self.assertTrue(check_mapping(left, right, [], {"a": "a", "b": "b"}))

    def test_directed_orientation(self):
        left, right = graph(True), graph(True)
        right["edges"][0][:2] = ["b", "a"]
        self.assertFalse(check_mapping(left, right, [], {"a": "a", "b": "b"}))

    def test_node_edge_labels(self):
        for kind in ("node", "edge"):
            right = graph()
            if kind == "node": right["nodes"][0]["label"] = "different"
            else: right["edges"][0][2] = "different"
            self.assertFalse(check_mapping(graph(), right, [], {"a": "a", "b": "b"}))

    def test_bijection_and_anchor(self):
        for mapping in ({"a": "a"}, {"a": "a", "b": "a"}, None):
            self.assertFalse(check_mapping(graph(), graph(), [], mapping))
        self.assertFalse(check_mapping(graph(), graph(), [["a", "b"]], {"a": "a", "b": "b"}))

    def test_empty_graph(self):
        empty = {"directed": False, "nodes": [], "edges": []}
        self.assertTrue(check_mapping(empty, empty, [], {}))
        self.assertEqual(inspect_graph(empty)["nodes"], 0)

    def test_graph_input_validation(self):
        for value in ({}, {"directed": 1, "nodes": [], "edges": []}):
            with self.assertRaises(ValueError): Graph(value)
        duplicate = graph()
        duplicate["edges"].append(["b", "a", "edge"])
        with self.assertRaises(ValueError): Graph(duplicate)
        with self.assertRaises(ValueError): check_mapping(graph(), graph(), [["a", "a"], ["a", "b"]], {})

    def test_jsonl_continues_after_error(self):
        data = "invalid-json\n" + json.dumps({"id": "sample", "graph": graph()}) + "\n"
        result = subprocess.run([sys.executable, "-m", "graph_catalog", "inspect"], input=data,
                                text=True, capture_output=True, cwd=Path(__file__).parents[1], check=True)
        rows = [json.loads(line) for line in result.stdout.splitlines()]
        self.assertEqual(rows[0], {"error": "invalid_request"})
        self.assertEqual(rows[1]["id"], "sample")
        self.assertEqual(rows[1]["edges"], 2)


if __name__ == "__main__": unittest.main()
