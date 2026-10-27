"""Small, dependency-free labelled graph input utilities."""
from collections import Counter


def _text(value):
    if not isinstance(value, str) or len(value.encode("utf-8")) > 128:
        raise ValueError("expected UTF-8 string of at most 128 bytes")
    return value


class Graph:
    def __init__(self, value):
        if not isinstance(value, dict) or set(value) != {"directed", "nodes", "edges"}:
            raise ValueError("invalid graph fields")
        if type(value["directed"]) is not bool or not isinstance(value["nodes"], list):
            raise ValueError("invalid graph type")
        if len(value["nodes"]) > 1024 or not isinstance(value["edges"], list):
            raise ValueError("graph limit or edges type")
        labels = {}
        for node in value["nodes"]:
            if not isinstance(node, dict) or set(node) != {"id", "label"}:
                raise ValueError("invalid node fields")
            node_id, label = _text(node["id"]), _text(node["label"])
            if node_id in labels:
                raise ValueError("duplicate node")
            labels[node_id] = label
        self.directed = value["directed"]
        self.labels = labels
        self.ids = tuple(sorted(labels))
        self.edges = {}
        self.edge_count = 0
        for edge in value["edges"]:
            if not isinstance(edge, list) or len(edge) != 3:
                raise ValueError("invalid edge")
            a, b, label = map(_text, edge)
            if a not in labels or b not in labels:
                raise ValueError("unknown endpoint")
            if (a, b) in self.edges:
                raise ValueError("parallel edge")
            self.edges[a, b] = label
            if not self.directed:
                self.edges[b, a] = label
            self.edge_count += 1


def inspect_graph(value):
    graph = Graph(value)
    histogram = Counter(graph.labels.values())
    return {"directed": graph.directed, "nodes": len(graph.ids), "edges": graph.edge_count,
            "self_loops": sum((node, node) in graph.edges for node in graph.ids),
            "node_labels": [{"label": label, "count": histogram[label]} for label in sorted(histogram)]}


def check_mapping(left, right, anchors, mapping):
    a, b = Graph(left), Graph(right)
    if not isinstance(anchors, list) or len(anchors) > 16:
        raise ValueError("invalid anchors")
    used_left, used_right = set(), set()
    for pair in anchors:
        if not isinstance(pair, list) or len(pair) != 2:
            raise ValueError("invalid anchor pair")
        x, y = map(_text, pair)
        if x not in a.labels or y not in b.labels or x in used_left or y in used_right:
            raise ValueError("invalid anchor endpoints")
        used_left.add(x)
        used_right.add(y)
    if not isinstance(mapping, dict):
        return False
    if set(mapping) != set(a.ids) or any(not isinstance(v, str) for v in mapping.values()):
        return False
    if a.directed != b.directed or set(mapping.values()) != set(b.ids) or len(set(mapping.values())) != len(a.ids):
        return False
    if any(a.labels[x] != b.labels[y] for x, y in mapping.items()):
        return False
    if any(mapping[x] != y for x, y in anchors):
        return False
    missing = object()
    return all(a.edges.get((x, y), missing) == b.edges.get((mapping[x], mapping[y]), missing)
               for x in a.ids for y in a.ids)
