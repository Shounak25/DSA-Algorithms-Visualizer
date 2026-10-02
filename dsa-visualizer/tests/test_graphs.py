import pytest

from dsa_visualizer.algorithms.graphs import (
    GRAPH_ALGOS,
    circle_layout,
    make_graph_frames,
    parse_edges,
)

EDGES = "A-B:4, A-D:2, B-C:3, B-E:7, D-E:1, C-F:5, E-F:2"


def run(algo, edges=EDGES, start="A", target="F"):
    nodes, adj, ed, _ = parse_edges(edges)
    return make_graph_frames(algo, adj, nodes, ed, circle_layout(nodes), start, target)


def test_parse_edges_basic():
    nodes, adj, edges, weighted = parse_edges(EDGES)
    assert nodes == list("ABCDEF")
    assert weighted and ("A", "B", 4.0) in edges


def test_parse_edges_keeps_lightest_duplicate_and_is_case_insensitive():
    _, _, edges, _ = parse_edges("a-b:5, B-A:2")
    assert edges == [("A", "B", 2.0)]


@pytest.mark.parametrize("bad", ["", "A", "A-A", "A-B:x", "A-B:-1", "A-B-C"])
def test_parse_edges_rejects_bad_input(bad):
    with pytest.raises(ValueError):
        parse_edges(bad)


def test_dijkstra_finds_shortest_path():
    result = run("Dijkstra")[-1]["result"]
    assert "A → D → E → F" in result and "cost = 5" in result


def test_astar_matches_dijkstra_cost():
    assert "cost = 5" in run("A*")[-1]["result"]


def test_no_path_reported():
    assert "No path" in run("Dijkstra", "A-B:1, C-D:1", "A", "D")[-1]["result"]


def test_bfs_visits_every_reachable_node_once():
    order = run("BFS")[-1]["visited"]
    assert sorted(order) == list("ABCDEF") and len(order) == 6


def test_components_counts_groups():
    last = run("Components", "A-B:1, C-D:1, E-F:1")[-1]
    assert "3" in last["result"] or "3" in last["status"]


@pytest.mark.parametrize("algo", GRAPH_ALGOS)
def test_every_algorithm_produces_frames(algo):
    assert len(run(algo)) > 1
