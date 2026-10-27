# Labelled Graph Catalog

A small original graph inspection utility, authored with AI assistance for a
repository-extension exercise. Python 3.11 or newer, standard library only.
It is not a fork, adapter, or implementation of a third-party graph API.

`Graph` reads simple directed or undirected labelled graphs. The input object
contains `directed`, `nodes` (`id`, `label`) and `edges` (`[from,to,label]`).
Labels and node IDs are UTF-8 strings of at most 128 bytes. Nodes are unique,
edge endpoints exist, parallel edges are rejected, and self loops are allowed.
An undirected edge has the same identity regardless of endpoint order.

`inspect_graph` returns node/edge/self-loop counts and a sorted node-label
histogram. `check_mapping` checks an explicitly supplied full correspondence
against both graphs and up to 16 anchor pairs. It does not discover mappings
or count possible correspondences. Calls leave their input objects unchanged.

Run the existing regression tests:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

The JSONL CLI supports these commands:

```sh
python3 -m graph_catalog inspect
python3 -m graph_catalog check
```

An inspect request has exactly `id` and `graph`. Its result contains `id` plus
the five inspection fields. A check request has exactly `id`, `left`, `right`,
`anchors`, and `mapping`; its result contains `id` and boolean `valid`.
Invalid input yields `{"error":"invalid_request"}` and the next line is still
processed. Empty lines are ignored. Each response is flushed immediately.

The repository has no network, external package, graph matcher, correspondence
counting command, generated task answer, or hidden-evaluation material.
